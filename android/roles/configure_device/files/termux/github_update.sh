#!/bin/bash

cd /storage/emulated/0/github/prod || exit;
git checkout main;
git reset --hard origin/HEAD;
git pull origin main -f;

exit 0;
