#!/bin/zsh

venvpath='/run/media/quentin/data/venv/python_mattermost_qkzk/'
scriptpath='/home/quentin/gdrive/dev/python/mattermost/robert_le_robot'

cd $venvpath
echo "The path for virtual environnment is :"
pwd
source venv/bin/activate

echo "The path for the python file is :"
cd $scriptpath
pwd

# echo "Launching the python file"
# python robert_le_robot.py
