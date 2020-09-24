# Project Alice skill kit

The Project Alice skill kit is a tool that helps creating skills for Alice.

It was formerly written by [maxbachmann](https://github.com/maxbachmann)

## Features
- Create new skills
- Validate the format of all json files

## Install
```bash
pip3 install projectalice-sk
```
The skill kit supports tab completion for `bash` and `zsh` it can be activated by adding this in your .bashrc:
```bash
eval "$(_ALICE_SK_COMPLETE=source projectalice-sk)"
```
For zsh users add this to your .zshrc:
```bash
eval "$(_ALICE_SK_COMPLETE=source_zsh projectalice-sk)"
```

## Testing
It is possible to run all validation tests we currently run against a skill when someone submits a PR locally using:
```bash
projectalice-sk validate --paths <pathnames>
```
Further information on the validation tests can be found [here](https://github.com/project-alice-powered-by-snips/ProjectAliceSkillKit/blob/master/Validation.md)


## Auto skills creation
To create the basic files needed for a skill to work run:

```bash
projectalice-sk create
```
This saves you the hassle of creating the directory tree, the required files and so on. It also follows the strict conventions we made for skills and will avoid you trouble when submitting your skill for review.
