# Alice Skill Kit

The Alice Skill Kit is a tool that helps creating Modules for Alice.

## Features
- [create a new Module](https://github.com/project-alice-powered-by-snips/ProjectAliceSkillKit/blob/master/CreateModules.md)
- [validate the format of all json files](https://github.com/project-alice-powered-by-snips/ProjectAliceSkillKit/blob/master/Validation.md)

## Install
```bash
pip3 install alice-sk
```

## Testing
Syntax of `dialogTemplate.json`, `talk.json` and `Module.install` files of all Modules is tested by travis using json Schemas. Further information on the tests and how to test the files locally can be found in [Tools/JsonValidator](https://github.com/project-alice-powered-by-snips/ProjectAliceModules/tree/master/Tools/JsonValidator).


## Auto modules creation
Downloading Tools/Moduler you can have a basic tool to create the basic needed files for a module to work. This saves you the hassle of creating the directory tree, the required files and so on. It also follows the strict conventions we made for modules and will avoid you trouble when submitting your module for review.