import subprocess
import os
import shutil
import asyncio
from pathlib import Path
import cv2
from wand.image import Image
import ffmpeg

SEMAPHORE_VIDEOS = False
SEMAPHORE_AUDIOS = False
SEMAPHORE_IMAGES = False

class TicketedDict(dict):
    def __init__(self, *args, **kwargs):
        self._ni = 0
        self.event = asyncio.Event()
        super().__init__(*args, **kwargs)
        
    def has_next(self):
        return self._ni in self
    
    async def wait(self):
        while not self.has_next():
            await self.event.wait()
            self.event.clear()
    
    async def pop(self):
        await self.wait()
        ret = super().pop(self._ni)
        self._ni += 1
        return ret
    
    def notify(self, *args, **kwargs):
        return self.event.set(*args, **kwargs)

def process_image(source, destination, distort):
    with Image(filename=source) as original:
        dst_width = int(original.width * (distort / 100.))
        dst_height = int(original.height * (distort / 100.))
        with original.clone() as distorted, open(destination, mode='wb') as out:
            distorted.liquid_rescale(dst_width, dst_height)
            distorted.resize(original.width, original.height)
            distorted.save(out)

async def process_frames(coro, queue_in, out_pile):
    while True:
        try:
            frame_data = await queue_in.get()
        except asyncio.exceptions.CancelledError:
            return
        nr = frame_data.pop('nr')
        await asyncio.to_thread(coro, **frame_data)
        queue_in.task_done()
        out_pile[nr] = frame_data['destination']
        out_pile.notify()

async def read_frames(capture, frames_distorted, frames_original, queue, tasks, distort_start, distort_end=None, distort_end_frame=None):
    frames_read = 0
    distort = distort_start
    if distort_end_frame is None:
        distort_end_frame = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    while True:
        read_ok, frame = capture.read()
        if not read_ok:
            break
        if distort_end is not None:
            distort = distort_start + (distort_end - distort_start) * (min(frames_read, distort_end_frame) / distort_end_frame)
        frame_filename = f'frame_{str(frames_read).zfill(32)}.png'
        frame_original = str(Path(frames_original) / frame_filename)
        frame_distorted = str(Path(frames_distorted) / frame_filename)
        cv2.imwrite(frame_original, frame)
        await queue.put({'source': frame_original, 'destination': frame_distorted, 'distort': distort, 'nr': frames_read})
        frames_read += 1
    await queue.join()
    for worker in tasks:
        worker.cancel()

async def write_frames(output, pile):
    while True:
        try:
            frame_distorted = await pile.pop()
        except asyncio.exceptions.CancelledError:
            return
        newframe = cv2.imread(frame_distorted)
        output.write(newframe)

async def distort_video(capture, output, distort_start, distort_end=None, distort_end_frame=None):
    output_pile = TicketedDict()
    Path('frames_distorted').mkdir(exist_ok=True)
    Path('frames_original').mkdir(exist_ok=True)
    frames_distorted = Path('frames_distorted')
    frames_original = Path('frames_original')
    capture_queue = asyncio.Queue(20)
    workers = [asyncio.create_task(process_frames(process_image, capture_queue, output_pile)) for i in range(10)]
    workers += [asyncio.create_task(write_frames(output, output_pile))]
    asyncio.create_task(read_frames(capture, frames_distorted, frames_original, capture_queue, workers, distort_start, distort_end, distort_end_frame))
    await asyncio.gather(*workers)

def distort_audio(distorted_video, in_audio, audio_freq, audio_mod, out_filename):
    video = ffmpeg.input(distorted_video).video
    audio = ffmpeg.input(in_audio).audio.filter("vibrato", f=audio_freq, d=audio_mod)
    (ffmpeg.concat(video, audio, v=1, a=1).output(out_filename).run(overwrite_output=True))
    subprocess.run(['ffmpeg', '-i', out_filename, '-t', '15', '-r', '24', '-vf', 'scale=-2:720', 'distorted.mp4', '-y'], check=True)

def distort_audiofile(in_audio, audio_freq, audio_mod, out_filename):
    audio = ffmpeg.input(in_audio).audio.filter("vibrato", f=audio_freq, d=audio_mod)
    audio.output(out_filename).run(overwrite_output=True)

def distortioner(input_filename, is_gif=False):
    global SEMAPHORE_VIDEOS, SEMAPHORE_AUDIOS, SEMAPHORE_IMAGES
    input_path = Path(input_filename)
    if input_path.suffix.lower() in ['.mp4', '.mov', '.avi']:
        while SEMAPHORE_VIDEOS:
            pass
        try:
            SEMAPHORE_VIDEOS = True
            subprocess.run(['ffmpeg', '-i', input_filename, '-t', '15', '-r', '24', '-vf', 'scale=-2:360', 'preprocessed.mp4', '-y'], check=True)
            capture = cv2.VideoCapture('preprocessed.mp4')
            fps = capture.get(cv2.CAP_PROP_FPS)
            video_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            video_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
            output = cv2.VideoWriter('tmp.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (video_width, video_height))
            asyncio.run(distort_video(capture, output, 60, None, frames - 1))
            capture.release()
            output.release()
            if is_gif:
                subprocess.run(['ffmpeg', '-i', 'tmp.mp4', '-vf', 'fps=10,scale=-2:360:flags=lanczos', 'distorted.mp4', '-y'], check=True)
            else:
                distort_audio('tmp.mp4', 'preprocessed.mp4', 10, 1, 'output.mp4')
        except Exception as e:
            print(e)
        finally:
            SEMAPHORE_VIDEOS = False
            if os.path.exists('preprocessed.mp4'):
                os.remove('preprocessed.mp4')
            if os.path.exists('tmp.mp4'):
                os.remove('tmp.mp4')
            if os.path.exists('output.mp4'):
                os.remove('output.mp4')
            shutil.rmtree('frames_distorted')
            shutil.rmtree('frames_original')
    elif input_path.suffix.lower() in ['.jpg', '.png']:
        while SEMAPHORE_IMAGES:
            pass
        try:
            SEMAPHORE_IMAGES = True
            process_image(input_filename, 'distorted.jpg', 25)
        except Exception as e:
            print(e)
        finally:
            SEMAPHORE_IMAGES = False
    elif input_path.suffix.lower() in ['.mp3', '.wav', '.ogg', '.oga']:
        while SEMAPHORE_AUDIOS:
            pass
        try:
            SEMAPHORE_AUDIOS = True
            distort_audiofile(input_filename, 10, 1, 'distorted.mp3')
        except Exception as e:
            print(e)
        finally:
            SEMAPHORE_AUDIOS = False
    else:
        raise ValueError("Unsupported file type")

if __name__ == '__main__':
    distortioner('IMG_6233.MP4')
