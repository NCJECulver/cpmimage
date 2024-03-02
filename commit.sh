#!/bin/bash

# Check if at least two arguments are given (# - number of positional parameters)
if [ $# -lt 2 ]; then
    echo "Usage: $0 branch 'commit message'"
    echo "Where branch is the branch you're commiting to; usually main or master"
    echo "commit message is just a message indicating the purpose of the commit"
    echo "If prompted, enter username NCJECulver and password of personal access token"
    exit 1
fi

# The first argument is the branch
branch="$1"

# Shift the first argument, leaving the rest as the commit message
shift
message="$*"

# Checkout or create the branch
git checkout -b "$branch" 2>/dev/null || git checkout "$branch"

# Add changes to staging
git add .

# Commit the changes
git commit -m "$message"

# Push to the remote repository
git push origin "$branch"

exit

If prompted for user/password, use NCJECulver and the generated personal access token.
PATs expire. If you find thats the case, generate a new one as follows:

    Log in to GitHub: Go to GitHub.com and log in with your account. You can use your account password from the webpage.
    Access Settings: Click on your profile picture in the top right corner, then click "Settings."
    Developer Settings: Scroll down to the bottom of the sidebar and click on "Developer settings."
    Personal Access Tokens: Click on "Personal access tokens" then "Generate new token."
    Token Description: Give your token a description so you can remember what it's used for.
    Select Scopes: Choose the scopes or permissions you'd like to grant this token. For general Git operations, selecting "repo" is usually sufficient.
    Generate Token: Click the "Generate token" button at the bottom of the page.
    Copy Your New Token: Make sure to copy your new personal access token now. You won’t be able to see it again!