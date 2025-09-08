#!/usr/bin/env python3
"""
Command Tracking Decorator

Provides a decorator to automatically track command executions and metrics.
"""

import time
import functools
import sys
from typing import Callable, Any, List
from pathlib import Path

from .metrics_collector import MetricsCollector


def track_command(command_id: str, cache_dir: Path = None):
    """
    Decorator to track command execution metrics.
    
    Args:
        command_id: Unique identifier for the command
        cache_dir: Cache directory path (defaults to .cb/cache)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Determine cache directory
            if cache_dir is None:
                # Try to find .cb directory
                current = Path.cwd()
                while current != current.parent:
                    cb_dir = current / '.cb'
                    if cb_dir.exists():
                        cache_dir_path = cb_dir / 'cache'
                        break
                    current = current.parent
                else:
                    # Fallback to current directory
                    cache_dir_path = Path('.cb') / 'cache'
            else:
                cache_dir_path = cache_dir
            
            # Initialize metrics collector
            collector = MetricsCollector(cache_dir_path)
            
            # Start timing
            start_time = time.time()
            success = False
            exit_code = 0
            
            try:
                # Extract command arguments for tracking
                command_args = []
                if args:
                    command_args.extend(str(arg) for arg in args)
                if kwargs:
                    command_args.extend(f"{k}={v}" for k, v in kwargs.items())
                
                # Execute the command
                result = func(*args, **kwargs)
                success = True
                return result
                
            except SystemExit as e:
                # Handle click's SystemExit for exit codes
                exit_code = e.code if e.code is not None else 1
                success = exit_code == 0
                raise
            except Exception as e:
                exit_code = 1
                success = False
                raise
            finally:
                # Record execution metrics
                end_time = time.time()
                collector.record_command_execution(
                    command_id=command_id,
                    start_time=start_time,
                    end_time=end_time,
                    success=success,
                    exit_code=exit_code,
                    args=command_args
                )
        
        return wrapper
    return decorator


def get_command_tracker(cache_dir: Path = None) -> MetricsCollector:
    """
    Get a metrics collector instance for manual tracking.
    
    Args:
        cache_dir: Cache directory path (defaults to .cb/cache)
    
    Returns:
        MetricsCollector instance
    """
    if cache_dir is None:
        # Try to find .cb directory
        current = Path.cwd()
        while current != current.parent:
            cb_dir = current / '.cb'
            if cb_dir.exists():
                cache_dir = cb_dir / 'cache'
                break
            current = current.parent
        else:
            # Fallback to current directory
            cache_dir = Path('.cb') / 'cache'
    
    return MetricsCollector(cache_dir)
