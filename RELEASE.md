# Release process

* Check what release version is set in [intel_variant_provider/__init__.py](intel_variant_provider/__init__.py). Adjust if needed.

* Set a Release Candidate (RC) tag (replace `0.0.3` with the actual release number):
```
git tag -a v0.0.3-rc1 -m "Intel Variant Provider Plugin v0.0.3 RC1"
git push origin v0.0.3-rc1
```

* Pushing the tag will trigger automated CI which will build the Python wheel package and post a Pre-Release at Github. Check for completeness at https://github.com/wheelnext/intel-variant-provider/releases.

* Download the package to [docs/intel-variant-provider/](docs/intel-variant-provider/):
```
wget -P docs/intel-variant-provider/ \
   https://github.com/wheelnext/intel-variant-provider/releases/download/v0.0.3-rc1/intel_variant_provider-0.0.3-py2.py3-none-any.whl
```

* Update [docs/intel-variant-provider/index.html](docs/intel-variant-provider/) by adding a reference to the new package.

* Push the package and updated index to the repository:
```
git add docs/
git commit -s -m "Upload v0.0.3-rc1 wheel" docs/
git push origin HEAD:refs/heads/main
```

* Pushing the new commit will trigger automated CI which will update repository Github pages and make new package available for download.

* Set a Release tag:
```
git tag -a v0.0.3 -m "Intel Variant Provider Plugin v0.0.3"
git push origin v0.0.3
```

* Pushing the tag will trigger automated CI which will post a Release at Github. Check for completeness at https://github.com/wheelnext/intel-variant-provider/releases.

* Adjust release message at https://github.com/wheelnext/intel-variant-provider/releases by providing release details.

