# -*- coding: utf-8 -*-
'''
=============
myr.discovery
=============

Discovery module for myrstack.
'''

import itertools

from celery import shared_task
from dogpile.cache import make_region


class TaskDiscovery:

    TASK_NAMES_CACHE_KEY = 'myr-tasks-names'
    TASK_DEFS_CACHE_KEY_FMT = 'def::{task_name}'

    def get_cache_region(self):
        return make_region().configure(
            "dogpile.cache.dbm",
            expiration_time=10,
            arguments={
                "filename": "/tmp/myr-discovery.dbm"
            }
        )

    @property
    def cache(self):
        if not hasattr(self, '_cache'):
            setattr(self, '_cache', self.get_cache_region())
        return getattr(self, '_cache')

    def get_task_def(self, task_name):
        task_def = self.cache.get(self.get_task_cache_key(task_name=task_name))
        return task_def

    def set_task_def(self, task_name, task_def):
        self.cache.set(
            self.get_task_cache_key(task_name),
            task_def)

    def get_announced_task_names(self):
        return self.cache.get(self.TASK_NAMES_CACHE_KEY) or ()

    def set_announced_task_names(self, val):
        self.cache.set(self.TASK_NAMES_CACHE_KEY, val)

    def get_task_cache_key(self, task_name):
        return self.TASK_DEFS_CACHE_KEY_FMT.format(task_name=task_name)

    def get_announced_tasks(self):
        return {
            task_name: self.get_task_def(task_name)
            for task_name in self.get_announced_task_names()}


@shared_task
def announce(tasks):
    task_discovery = TaskDiscovery()
    cached_task_names = task_discovery.get_announced_task_names()
    for task_name, task_def in tasks.items():
        task_discovery.set_task_def(task_name, task_def)
    task_discovery.set_announced_task_names(
        {task_name for task_name
         in itertools.chain(cached_task_names or [], tasks.keys())})


@shared_task
def discover():
    return TaskDiscovery().get_announced_tasks()
