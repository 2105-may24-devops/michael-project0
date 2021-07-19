# Recipe Recorder

## Project Description

A console application that manages and stores recipes in a standardized file format to allow a user to collect recipes from many different sources, and store them in a distributed digital cookbook. Users can interactively create, read, update and delete recipes from the command line, as well as automate the commands through a script file. The application can be tested, installed and run in a virtual environment remotely with automation tools.

## Technologies Used

- Automation
  - Ansible
  - Bash
- Build
  - Python

## Features

### Implemented Features

- Kubernetes-style command format implemented (Verb Noun Args)
- CRUD operations are functional
- Recipe ingredients can be converted to different units
- Markdown output
- JSON serialization

### Planned Features
- Better implementation of recipe unit conversions for common ingredients
- Better implementation of branch policies in development
- Output function may have unexpected side effects

## Getting Started

The main entrypoint to the program is in `app.py`. You may want to use a `venv` to deploy the dependencies listed in `requirements.txt`.

There is an ansible playbook that will allow you to deploy and test the application onto a VM. The inventory file and ssh keys need to be set up before ansible can run.

## Usage

The console application has two modes: file mode and recipe mode. In file mode, the commands look similar to bash commands for navigating the file-system (cd, pwd, ls, etc.). They may have less functionality than the usual bash command. In recipe mode, the command syntax borrows from kubernetes, starting with a verb, then a noun, then any arguments.


## License

Copyright 2021 Michael Darmawan

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

