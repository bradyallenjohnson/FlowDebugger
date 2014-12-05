#!/usr/bin/env python

from distutils.core import setup

setup(name='FlowDebugger',
      version='1.0',
      description='Debug Open Flow Switch FlowEntries',
      author='Brady Johnson',
      author_email='bradyallenjohnson@gmail.com',
      url='https://github.com/bradyallenjohnson/FlowDebugger',
      packages=['FlowDebugger', 'FlowDebugger/Flows', 'FlowDebugger/Gui'],
      scripts=['bin/flow_debugger']
     )

