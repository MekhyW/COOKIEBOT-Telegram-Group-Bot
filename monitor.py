#!/usr/bin/env python3
"""
COOKIEBOT Docker Container Monitor
This script monitors Docker containers for resource usage and health status,
automatically restarting containers that exceed resource limits or become unhealthy.
"""

import docker
import time
import logging
import json
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ContainerMonitor:
    def __init__(self, check_interval: int = 30):
        self.client = docker.from_env()
        self.check_interval = check_interval
        self.restart_counts = {}
        self.max_restarts_per_hour = 5
        self.cpu_threshold = 80.0  # CPU percentage
        self.memory_threshold = 90.0  # Memory percentage
        
    def get_cookiebot_containers(self) -> List[docker.models.containers.Container]:
        try:
            containers = self.client.containers.list(filters={'name': 'cookiebot-instance'})
            return containers
        except Exception as e:
            logger.error(f"Error getting containers: {e}")
            return []
    
    def get_container_stats(self, container) -> Optional[Dict]:
        try:
            stats = container.stats(stream=False)
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
            cpu_percent = 0.0
            if system_delta > 0 and cpu_delta > 0:
                cpu_percent = (cpu_delta / system_delta) * len(stats['cpu_stats']['cpu_usage']['percpu_usage']) * 100.0
            memory_usage = stats['memory_stats']['usage']
            memory_limit = stats['memory_stats']['limit']
            memory_percent = (memory_usage / memory_limit) * 100.0
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'memory_usage_mb': memory_usage / (1024 * 1024),
                'memory_limit_mb': memory_limit / (1024 * 1024)
            }
        except Exception as e:
            logger.error(f"Error getting stats for {container.name}: {e}")
            return None
    
    def check_container_health(self, container) -> bool:
        try:
            container.reload()
            health = container.attrs.get('State', {}).get('Health', {})
            status = health.get('Status', 'unknown')
            return status == 'healthy'
        except Exception as e:
            logger.error(f"Error checking health for {container.name}: {e}")
            return False
    
    def should_restart_container(self, container_name: str) -> bool:
        now = datetime.now()
        if container_name not in self.restart_counts:
            self.restart_counts[container_name] = []
        self.restart_counts[container_name] = [ # Remove restarts older than 1 hour
            restart_time for restart_time in self.restart_counts[container_name]
            if (now - restart_time).seconds < 3600
        ]
        return len(self.restart_counts[container_name]) < self.max_restarts_per_hour
    
    def restart_container(self, container) -> bool:
        try:
            if not self.should_restart_container(container.name):
                logger.warning(f"Container {container.name} has been restarted too many times in the last hour")
                return False
            logger.info(f"Restarting container {container.name}")
            container.restart()
            self.restart_counts[container.name].append(datetime.now()) # Record restart time
            time.sleep(10) # Wait for container to start
            container.reload()
            if container.status == 'running':
                logger.info(f"Container {container.name} restarted successfully")
                return True
            else:
                logger.error(f"Container {container.name} failed to start after restart")
                return False
        except Exception as e:
            logger.error(f"Error restarting container {container.name}: {e}")
            return False
    
    def restart_via_compose(self, service_name: str) -> bool:
        try:
            result = subprocess.run(
                ['docker-compose', 'restart', service_name],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                logger.info(f"Service {service_name} restarted via docker-compose")
                return True
            else:
                logger.error(f"Failed to restart {service_name} via docker-compose")
                return False
        except Exception as e:
            logger.error(f"Error restarting service {service_name}: {e}")
            return False
    
    def monitor_containers(self):
        """
        Main monitoring loop.
        """
        logger.info("Starting COOKIEBOT container monitoring")
        while True:
            try:
                containers = self.get_cookiebot_containers()
                if not containers:
                    logger.warning("No COOKIEBOT containers found")
                    time.sleep(self.check_interval)
                    continue
                for container in containers:
                    try:
                        container.reload()
                        if container.status != 'running':
                            logger.warning(f"Container {container.name} is not running (status: {container.status})")
                            continue
                        stats = self.get_container_stats(container) # Get resource statistics
                        if not stats:
                            continue
                        cpu_exceeded = stats['cpu_percent'] > self.cpu_threshold
                        memory_exceeded = stats['memory_percent'] > self.memory_threshold
                        is_healthy = self.check_container_health(container)
                        logger.info(
                            f"{container.name}: CPU: {stats['cpu_percent']:.1f}%, "
                            f"Memory: {stats['memory_percent']:.1f}% "
                            f"({stats['memory_usage_mb']:.1f}MB/{stats['memory_limit_mb']:.1f}MB), "
                            f"Healthy: {is_healthy}"
                        )
                        restart_needed = False
                        restart_reason = []
                        if cpu_exceeded:
                            restart_reason.append(f"CPU usage {stats['cpu_percent']:.1f}% > {self.cpu_threshold}%")
                            restart_needed = True
                        if memory_exceeded:
                            restart_reason.append(f"Memory usage {stats['memory_percent']:.1f}% > {self.memory_threshold}%")
                            restart_needed = True
                        if not is_healthy:
                            restart_reason.append("Container is unhealthy")
                            restart_needed = True
                        if restart_needed:
                            reason_str = ", ".join(restart_reason)
                            logger.warning(f"Restarting {container.name} due to: {reason_str}")
                            service_name = container.name.replace('cookiebot-instance-', 'cookiebot-')
                            if not self.restart_via_compose(service_name): # Try compose restart first, then direct restart
                                self.restart_container(container)
                    except Exception as e:
                        logger.error(f"Error monitoring container {container.name}: {e}")
                        continue
                
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.check_interval)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='COOKIEBOT Docker Container Monitor')
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=30,
        help='Check interval in seconds (default: 30)'
    )
    parser.add_argument(
        '--cpu-threshold',
        type=float,
        default=80.0,
        help='CPU usage threshold percentage (default: 80.0)'
    )
    parser.add_argument(
        '--memory-threshold',
        type=float,
        default=90.0,
        help='Memory usage threshold percentage (default: 90.0)'
    )
    args = parser.parse_args()
    monitor = ContainerMonitor(check_interval=args.interval)
    monitor.cpu_threshold = args.cpu_threshold
    monitor.memory_threshold = args.memory_threshold
    try:
        monitor.monitor_containers()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()