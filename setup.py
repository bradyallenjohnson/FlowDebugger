#!/usr/bin/env python

from distutils.core import setup

setup(name='FlowDebugger',
      version='1.1',
      description='Debug Open Flow Switch FlowEntries',
      author='Brady Johnson',
      author_email='bradyallenjohnson@gmail.com',
      url='https://github.com/bradyallenjohnson/FlowDebugger',
      packages=['FlowDebugger', 'FlowDebugger/Flows', 'FlowDebugger/Gui'],
      requires=['paramiko'],
      scripts=['bin/flow_debugger']
     )

