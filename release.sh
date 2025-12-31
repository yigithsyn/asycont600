ver=`(sed -n 's/^__version__ = "\(.*\)"/\1/p' src/asycont600/__init__.py)`
git tag v$ver && git push origin v$ver

# delete tag
# git tag -d v0.0.0
# git push --delete origin v0.0.0