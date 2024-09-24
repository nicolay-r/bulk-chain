## Publishing Release

Navigate to the root folder of this project and execute:
```bash
python3 setup.py sdist bdist_wheel
twine check ./dist/*
twine upload ./dist/*
```