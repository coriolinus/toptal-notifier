# create an archive with all git-tracked files
# note that we add two untracked files manually
(
   echo "config.toml"
   echo "persist.toml"
   git ls-files
) | xargs tar -cjf notify.tar.bz2
# examine the created file
tar -tvjf notify.tar.bz2
du -h notify.tar.bz2
