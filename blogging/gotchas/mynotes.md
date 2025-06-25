
# Really Long Notes!

---
### How to introduce line breaks in markdown?
use   
- \ 
- `&nbsp;`
-   Two spaces
- Double Tab (seems to work for me!)

For more details, refer [Basic Formatting on Github](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax).   

---

### How to present code in markdown?
Use either 3 backlashes for large pieces of code or single backlash for a single line of code.

Example Main code:      
```
  public static void main(){
    //Something goes here..
  }
```

Example single line code:     
`Drawing d = new Drawing`

---

### How to preview markdown in VS code?

Cmd + Shift + V (separate tab)    
Cmd + K + V   

---

### How to paste data in excel without losing any formatting?
First convert the cells to "Text" type.   
Then use Paste >Paste Special ( see screenshot) and select "Text".   

Very useful while copying data from .dta files (like RoutingTable.dta,etc) or copying from Kibana.  
Without this, we lose the formatting of the data like cctransid numbers get truncated.  

---

### Rainbow CSV plugin in vscode

Use "Align CSV columns" from command pallete to view the data in aligned way. you can easily see what data is under which column.

Use "Shrink CSV"  to see it in normal mode without extra spaces.

---

### How to view whats in a particular git stash?
Example: git stash show -p stash@{1}

---

### git diff
To know what's different between current branch and upstream/develop branch \
`git diff upstream/develop`   

To know a particular file diff with respect to HEAD    
`git diff HEAD $filename`   

To diff against upstream/develop a particular file    
`git diff upstream/develop src/main/java/com/organization/ace/mapstruct/PaymentMessageToXomMapping.java`    

---
### git stashing

To save it to a name, use:      
`git stash save "enableRuleTrace"`

To list all stashes:      
`git stash list`

To apply a stash and keep it in stash stack:   
`git stash apply stash@{n}`


To apply a stash and remove it from the stash stack:    
`git stash pop stash@{n}`

To drop a particular entry,    
`git stash drop stash@{n}`

[advanced]      
`git checkout stash -- .`

This will restore all the files in the current directory to their stashed version.    

Show a particular file in git stash:    
`git show stash@{0}:paymentauthorizationservTests/src/test/resources/datasheets/AddCard/pas-auth-OMNIPAY_RBS_ADDCARD.csv`

Stash only particular files    
`git stash --patch`
use `a` to stash the whole file and `d` to ignore that file.    

Checkout a single file from the stash:    
`git checkout stash@{0} -- filename`

Checkout a single file from stash to a different file: non-destructive approach      
`git show stash@{0}:stashed_file.rb > copy_of_stashed_file.rb`


How to checkout a particular commit?   
First you checkout the commit-sha and then create a new branch(say feature) from that commit.   
For example:   
`git checkout commit-sha`   
`git checkout -b feature.`

---


### How to undo all uncommitted changes in git

    git reset   
reset will unstage all the file which you might have added with git add.   

    git checkout .   
this one will revert all uncommitted local changes   


---

### git cleanup

    git stash save temp   
    git clean -fd   
    git status   
//at this point it should be a clean working tree   

---

### pushing to new branches

Sample:    

      git push -u origin OFFUSCounter   

---

### How to checkout  from some other branch
Sample: 
```
git remote add manramadoss git@github.organization.com:manramadoss/Rules.git
git remote -v
git fetch manramadoss
git checkout -b someBranch manramadoss/someBranch

```

---

### Git delete branch

// delete branch locally

      git branch -d localBranchName   

// delete branch remotely

      git push origin --delete remoteBranchName   

---

### How to force reset a branch to look exactly like upstream branch?

Let's say i messed up the develop branch. 

      git reset --hard upstream/develop
      git push origin develop -f

---
### How to use nvm

nvm stands for node version manager.      
It can be used to switch between node versions.     

Add the below line to .zshrc 

      export NVM_DIR="$HOME/.nvm"
      [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

---

### VSCode hack

- To open a file in VSCOde, use Command + P
- To open a file in new tab, use Option + Enter.
- To go back to previous selection, ctrl + -

---

### gh tool 

To checkout a PR itself, one can do:      
```
gh pr checkout 1957
``` 

Alternately you can find out the person's branch and checkout that branch onto your local.      

---

### How to reset a branch to look exactly like upstream branch?

Let's say i messed up the develop branch.     
```
git reset --hard upstream/develop   
git push origin develop -f    
```
---

### intellij issues: 

intellij not picking up the right jar   
- deleted the corresponding folder in .m2   
- reimported the project    
- the latest jar got picked up.   

---

### intellij writing classes issue

Issue was that it was taking forever while doing "writing classes" in intellij

Below steps worked for me:
- Build, Execution, Deployment -> Compiler -> Java Compiler
- Uncheck "Use compiler from module target JDK when possible"
- Increase build process heap to 2000

---

### intellij shortcuts

- cmd + 7: to see the list of methods , say in a java class.      
- ctrl + option +H : to see call hierarchy      
- Cmd + Shift + p (created custom): View Breakpoints.   

---

### how to bypass safety check in chrome?

"thisisunsafe" is a BYPASS_SEQUENCE for Chrome version 65
"badidea" Chrome version 62 - 64.
"danger" used to work in earlier versions of Chrome

console.log(window.atob('dGhpc2lzdW5zYWZl')); //it prints thisisunsafe

Type "thisisunsafe" when you face certificate invalid issue.
Do this for websites which are well trusted like organization internal ones.


---

### How to add cert

Certificate Hacks
Here is a hack that worked for me. It extracts the proxy cert chain by making a test connection to google.com.

Note: Run this command while inside corp network/VPN

- Step 1
```
mkdir -p ~/certs && echo -n | openssl s_client -showcerts -connect google.com:443 | sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > ~/certs/organization-proxy-chain.pem && export NODE_EXTRA_CA_CERTS=~/certs/organization-proxy-chain.pem
```
Step 2 is Optional

- Step 2: add below line to the bash ~/.profile
``` 
  export NODE_EXTRA_CA_CERTS=~/certs/organization-proxy-chain.pem 
```
In future, there is a chance one or more of the intermediate cert files downloaded here is expired. If, then re-run the Step 1 above

---

### how to create a bookmarklet
Create a bookmarklet for showing essential details from CAL page.
Since it already has jquery, you need to append probably a modal to the dom.

https://medium.com/@jkirchartz/scrape-any-web-page-with-a-2-clicks-and-a-little-css-896d4eceb0a6

---

### Steps to resolve intellij issues while running RaptorApplication

The best way to reset everything.     
`git clean -fdx`      
Now re-build the project in Intellij itself ( mvn clean install -skipTests)     
Now re-import the projects ( it's a button in the maven build menu).      
You need to increase heap-size again in intellij to 4000 or above.      
It should run the Raptor Application.

This should solve the issue.      
Additionally if some compile error happens during app start, try the followng:
- figure out which jar caused the issue
- delete that jar from .m2 repo
- retry the above steps.


---
### Removing corrupt jars
Remove lastupdated corrupted jars (don't use it often!)   
find ~/.m2 -name \*.lastUpdated -exec rm -fv {} +   
instead use -U option in mvn.   

---

### How to debug a maven test in Eclipse

https://doc.nuxeo.com/corg/how-to-debug-a-test-run-with-maven/      

Add -Dmaven.surefire.debug to debug in Eclipse      

Open the Debug Configuration in Eclipse and set up a remote application on port 5005.       

Run the configuration. The test will resume. You can use break points and all the usual features of Eclipse debugging.      

If you see the following error:     
 `org.apache.maven.surefire.booter.SurefireBooterForkException: There was an error in the forked process`

 Try removing target folder. it worked for me in most cases.    
 rm -rf ./target    

Sample code to start debugging from console:     
 `mvn test -Pcomponent-test-only -Dmaven.surefire.debug -DsuiteXmlFile=src/test/resources/testsuite/pr-failed-testsuites/failed-testsuites.xml -Durl=https://msmaster.qa.organization.com:14600/ -DmaxRetryCount=0 -Dmode=NORMAL`   

---

### How to zip in mac terminal?
`zip -r mynewfilename.zip foldertozip/ `


---
### Maven Exception during FT TestNG runs:

In case you face some maven exceptions while running the testNG, the below seems to work:     
`rm -rf ./target`

Also try running other testNG XML files and see if the error still happens.     

---
### Git CherryPicking

git cherrypick for rules tracing      
commit-id: 308d8cf12f452bf61bcc834ad2f55ad3f70c434f     

`git cherry-pick 308d8cf12f452bf61bcc834ad2f55ad3f70c434f`

Suppose you want to cherry pick without committing:     
`git cherry-pick -n <HASH>`

---

### check for any process using port 
`lsof -i tcp:3000`

---

### Decode 
Decode gzip encoded string quickly using terminal:    

Under Linux, you can confirm this works with:   

```
echo 'H4sIAAAAAAAAAEtUKC4pysxLV8hPU0jOSCxKTC5JLSoGAOP+cfkWAAAA' | base64 -d | gunzip
```
(Please note that on OSX, you should use `base64 -D` instead of `base64 -d` in the above command)

---

### VIM hacks

Append comma to end of every line:
```
:%s/$/\,/g
```
To comment all lines in a file in vi:
```
:%s/^/#/
```
To uncomment
```
:%s/^#//
```

---
### How to clear an app log and append new data to it.

Try logging in append >> mode in Linux. This way you can truncate your output and try fresh testcases.

```
: > log && cmd >> log
```
This will start with a empty file.

For example  
```
mvn spring-boot:run >> app.log
```

To clear the log,  
```
: > app.log  
```
This way you can flush out the log before every FT or any request and see the new entries in the log specific to your call.

---


### To disable automatic sleep in MAC so that I can have continous VPN access
`sudo pmset -a sleep 0`   

To make it sleep after 30 mins:   
`sudo pmset -a sleep 30`    

Explanation of the command:   
- pmset: command is to manipulate power management settings.    
- -a:  specifies that the setting applies for all conditions (power & battery)    
- sleep: configure system sleep timer   
- 0 : to disable    

This does reduce Mac's battery time significantly. So use when required.    

---

### Enable Debugging locally from command-line for Spring boot:
```
mvn spring-boot:run -Drun.jvmArguments="-Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=8009"    
```
Now connect to 8009 in Eclipse  in remote config.   

---

### How to disable back in Chrome when using two finger swipes..
Use below setting:

```
defaults write com.google.Chrome AppleEnableSwipeNavigateWithScrolls -bool FALSE
```
---

### VPN hosts update 

As per the developer doc , I have modified hosts entry is as follows:
Here’s an example /etc/hosts entry on Mac:
```
      127.0.0.1  localhost
      127.0.0.1  localhost.organization.com
```
Whenever we connect to VPN, the `/etc/hosts` file gets overwritten.
we need to separately add `localhost.organization.com` entry below localhost entry.

---

### Problem: No Xcode or CLT version detected!

`xcode-select --print-path`
in my case /Library/Developer/CommandLineTools

the next line deletes the path returned by the command above      
`sudo rm -rf $(xcode-select --print-path)`

install them (again) if you don't get a default installation prompt     
`xcode-select --install`

---
### NVM Installation

Installed node using NVM:     
```javascript
nvm install stable
nvm alias default stable
nvm ls-remote
nvm ls 
```
To choose a version, use:       
`nvm use 10.9.0`

```
npm build (whenever you change a node version)
```
---

### NPM debugging issues.
`npm i --loglevel verbose`      
 Use above to see detailed logs.

---
### Babel Fixes
You should add @babel/runtime as dependency to your package.json at client.     
```
npm install --save-dev @babel/plugin-transform-runtime
npm install --save @babel/runtime
```

---    

### Eclipse Hack   
`Copy Qualified Name` in Eclipse copies the path.     

---

### How to search in vi editor?

in command mode, press `/` to begin search.
- type the word you want to search    
- press n to see the next result    
- press N to see the previous result    


---

### intelligent grepping

Find text only in specific file types/extensions – Returns all the search results     
  `grep -ir --include=\*.py text_to_search`

Search for all xml files having word mastercard:    
  `grep -rli --include=\*.xml "mastercard*" .`

some other examples:  
Recursively search for 'ach.on' string in the current directory   
  `grep -r 'ach.on' .`

Search for MasterCard in PAS-Tests and get list of csvs:  
  `grep -rl "MasterCard" . | grep  ".csv" | grep -v "target"`


---
### Linux math operations

- Either `$(())` or `$[]` will work for computing the result of an arithmetic operation.      
- You're using $() which is simply taking the string and evaluating it as a command.      
- It's a bit of a subtle distinction. Hope this helps.      

As tink pointed out in the comments on this answer, $[] is deprecated, and $(()) should be favored.   

---

### How to replace & with newline in vscode?

- Enable regex search in find. ( last option showing .*)    
- now find and replace '&' with '\n'    

---

### How to find a particular file in a repo in github?
- Example: `org:Settlement-R file:TransactionTypeCode.java`

- So it's org and file filter.    


---

### Paste without formatting

- macOS lets you paste text without its original formatting.    
- Instead of pressing “Command+V”, press “Option+Shift+Command+V” to paste text without any formatting.   

---

### How to create a bookmarklet?

- First write your vanilla JS function  
- Then convert it to Immediately-invoked Function Expression (IIFE)   

```
(function(){
  //your code goes here
}) ();
```

- Then minify it   
- Then encode it   
- The encoded version can be placed as a url href in any page.   
- User can then drag-and-drop this &lt;a&gt; link to his bookmarks.  
 
---

### Mac tip:

- Ctrl + left/right arrow to switch between windows

---

### how to open a new tab in terminal (with same folder)?

- Command + T

---

### How to view remote debug java map object as JSON in Intellij?

In Expressions, try:      
  `JSONObject.toJSONString(your_map_object)`

Useful for noting down things!      

---

### convert observable to a list

```java
List<T> myList = myObservable.toList().toBlocking().single();
```

---

### How to sort a particular folder and view in human readable form?
`du -hs * | sort -h`

---

### postman SSO based:

Enter “organizationcorp” as your team domain on the enterprise login    

---

### How to clear cookies in Chrome?
Use the below command: 

`Cmd +shift + del`

---

### Run postman from the command-line:    
```
brew install newman
newman run -k organization_Sale_Refund.postman_collection.json -e E2E.postman_environment.json -d sale_paysecure.csv
newman run -k organization_Sale_Refund.postman_collection.json -e UAT.postman_environment.json -d sale_paysecure.csv
```

---
### Postman Shortcuts!

- `Command + Option + 0` : collpase json in the editor    
- `Beautify`: To prettify the json    


### How to collapse all folders in postman collection?    
- Note: This is a Hack!   
- type "a" or something in the collection search and then delete it.    


### How to look for references of a postman variable?   
- use Find/Replace. 
- It'll show all places where that variable is referenced.    

---

### Intellij speed up
Specify build heap size to 4096.

---

### Try this in intellij for workspace issue
- Close IDE like Intellij
- Try doing a git clean: 
```bash
git clean -xdf 
```
- File -> Invalidate Caches

----

### VSCode Diff View

In VSCode, we can check the diffs easily by going to Source Control and then looking in "Changes"

---

### How to do a branch compare locally?

Sometimes it's nice to do a review locally.   
say you are in branch A and you want to merge to branch B.    

Then we can give:   
`git diff A..B`   
Notice the dotted(..) notation. 

For example,    
`git diff develop..rd_final`    

diff produces a less output.    

Now search for "diff" using :   
`/^diff`    

After that, press n to see the next result and N to see the previous result.    
This is essentially a local review without a PR!    

---
### Git Squashing

Squash all the commits into a single commit   

```
git fetch upstream develop
git reset --hard upstream/develop
git merge --squash origin/UT_Coverage
git commit -m “UTs”
git push -f origin UT_Coverage
```

---

### How to revert a git commit without committing?

`git revert -n <commit-sha>`    

- Then reverted files will be appear in the staging area.     
- You can then review and commit.

---

### Cert issue in VPN
- Access was denied by the access policy.       
- This may be due to a failure to meet access policy requirements.      

- Go to Self Service :      
  - self-service: > Run “Certificate Cleanup”   


---
### How to know the blame quickly for a particular file?

- Go to a line, and click "Annotate" in Intellij.
Or 
- Go to github and go to "blame" section. Whichever line you want, hover over it. You'll see the PR which introduced that change.

---

### How to start a simple HTTP server from any directory?

This is usually useful to solve CORS issues on local.     

```
cd $working_dir
python -m SimpleHTTPServer
```
---

### How to know git history of a deleted file

`git log --follow "**/file_name_here.mdx"`    
- Press Enter/Return multiple times.    
- You'll see a list of commits with the author and time.     
- Now check it up in the pull requests based on author and time to arrive at matching PRs.      

---


### How to use visual studio as editor and diff viewer?

https://www.roboleary.net/vscode/2020/09/15/vscode-git.html     

For global settings: 
`git config --global -e`    

For local specific to the project, skip the --global flag ( it would be under project/.git/config)    
`git config  -e`    

```
[core]
  editor = code --wait
[diff]
  tool = vscode
[difftool "vscode"]
  cmd = code --wait --diff $LOCAL $REMOTE
[merge]
  tool = vscode
[mergetool "vscode"]
  cmd = code --wait $MERGED
```
Individually we can try these options as follows:   

To set the editor as VSCODE   
`git config --global core.editor 'code --wait'`     

Open in new window each time    
`git config --global core.editor 'code --wait --new-window'`

If you wish to revert back,     
`git config --global --unset core.editor `

To set the diff editor      
```
git config --global diff.tool vscode
git config --global difftool.vscode.cmd 'code --wait --diff $LOCAL $REMOTE'
```
Reference:
https://www.roboleary.net/vscode/2020/09/15/vscode-git.html     
  

---

### How to install homebrew:

Disable SSL verification    
```bash
git config --global http.sslverify false
```
Now run with --insecure option:     
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh) --insecure"
```

Now after you have done the installation, turn it back on:      
```bash
git config --global http.sslverify true
```

---

### How to change shell to bash?
```bash
chsh -s /bin/bash
```
---

### How to start eclipse with a custom config

`./eclipse -configuration /Users/kkailasnath/Documents/eclipse_config`      

---

### Optionally disable CrashPlan Code42 

Lot of data is being used for backing up.     
This might affect internet speed as well.   

So,   

To Stop Code42:   
`sudo launchctl unload /Library/LaunchDaemons/com.code42.service.plist`   

To Start Code42:    
`sudo launchctl load /Library/LaunchDaemons/com.code42.service.plist`   

To check if it's running or not:    
`ps auxww | grep -i Code42Service`    

We can use onedrive for taking backups if needed.   

---

### How to see signal strength in WIFI network?

In Mac, Hold Option key and click Network icon.     
You'll see RSSI value.      
Generally closer to 0 means strong network and closer to -100 means weak network.     
If RSSI value is less than -70 dBm, then it is a poor connection.     

---
### How to do auto-import in Intellij
- You can change the settings on your intelliJ.     
- Got to: `Preferances --> Editor --> General --> Auto imports`
- then make sure that the `Add unambiguous imports on the fly` checkbox is checked.    
- Alternately, you can try `shift+alt+enter`

---
### Avoid Github 'Squash and merge'
- Try to squash your commits in your branch. 
- Avoid Github's 'squash and merge' as it sometimes creates additional commits!

----

### How to go to super-class and implementation-classes in Intellij
- Cmd + U -> superclass
- Cmd + Option + B  -> subclass/implementation

---

### main and master are entirely different commit histories.

If the problem is "main and master are entirely different commit histories.", the following will work     
git checkout master   
git branch main master -f    
git checkout main   
git push origin main -f   

---

### How to push existing repo to another repo

Create a new repo at github.    
Clone the repo from fedorahosted to your local machine.   
git remote rename origin upstream   
git remote add origin URL_TO_GITHUB_REPO    
git push origin master    

---

### how to fix auto-complete issues in MacOS
autoload -Uz compinit && compinit

---
### How to switch java version
```
java -version 
```

openjdk version "1.8.0_232" ( the one i have used for a long time!)

Now run the following

```
/usr/libexec/java_home -V

export JAVA_HOME=`/usr/libexec/java_home -v 17.0.8`
```

---

###  Java17 Tweaks to make it work in Intellij

Added below VM args in Intellij after moving the project to Zulu 17

```bash
-Djava.net.preferIPv4Stack=true -Xmx8192M -Xms512M -XX:MetaspaceSize=512M -XX:MaxMetaspaceSize=4096M --custom-providers=customjsse
```
### How to add cow 
Added wowo and cow files as per this doc : https://github.organization.com/pages/RaptorFrameworkTools/RaptorDocumentation/4.5.x/RaptorPlatform/docs/mds/HTAccessCOWCornerOfWorld/#setup-local-cow

The cow and wowo files for this app ncpreferenceserv are available in dropzone.

---

## Ideas around how to reset a mistaken commit in your local 

Please use the below code with caution as it may potentially undo your changes!

A better approach could be to use git revert.

```
git add some_folder_by_mistake/
git commit -m "mistake!"
git reset HEAD~ # same as git reset HEAD~1
```

When you do a git reset HEAD~1, you tell Git to move the HEAD pointer back one commit. 

But (unless you use --hard) you leave your files as they were. 

So now git status shows the changes you had checked into C. You haven't lost a thing!

```
rm -rf some_folder_by_mistake/ #remove that mistaken folder
git log 
```

You are back to the previous HEAD now.

Use the --hard with more caution!

git reset --hard HEAD~1

Because you used --hard, your files are reset to their state at commit B.

---

### Python Notebooks VSCode Gotchas

To run a notebook, I first created a python environment with a python runtime in VSCode.

    Python version I selected: Python 3.12.6

Since most of the code examples covered in Andrew's course use older version of openai, 

here are few additional steps to use the older version:

To install in notebook, use the following commands in a cell: 

```
%%capture
!python -m pip install openai==0.27.0
!python -m pip install python-dotenv
```

---
### Cloning and running a python project using terminal

First create an environment using : 

```
python3 -m venv .venv
```

Then activate: 

```
source .venv/bin/activate
```

Now, install the dependencies using:

```
pip install -r requirements.txt
```

python3 test_claude.py

---

### How to copy file contents to clipboard without opening it

Here's how you can do it using `pbcopy` in Mac.

```
cat LLD_VendingMachine_Solution.md | pbcopy
```
---

### Some super-useful shortcuts in Markdown in Github

Below are some proven time-saver hacks to format faster in markdown!!

- Bold : `Command + B`
- Italic : `Command + I`
- Creating a Link : `Command + K`

- Ordered List: `Command+Shift+7`
1. Apples
2. Oranges

- Unordered list: `Command+Shift+8`
  - Apples
  - Oranges

- Quote : `Command+Shift+.
`>   This is a sample quote
  
See [keyboard-shortcuts](https://docs.github.com/en/get-started/accessibility/keyboard-shortcuts)

## Linux Mint Paste doesn't work in terminal issue
Use `Ctrl + Shift + V`, it worked!

### Cycle windows for apps
- To cycle between windows in vscode, simply press ctrl + w
- To cycle between windows in chrome, simply press command + ~ 

### How to enable word wrap in VSCode for notebook output in Mac?
- Set Word Wrap:
1.   Open the settings (Command+,) and search for notebook.output.wordWrap.
2.   Set the value to true.

---

### How to make git always ignore mac special file like .DS_Store
We could do using: 
```bash
git config --global core.excludesfile ~/.gitignore_global
echo ".DS_Store" >> ~/.gitignore_global
```

---

### How to remove all ignored files in git

Use below command carefully as you can't recover the files!
```bash
git clean -fdX
```

---

### How to ignore a particular extension in .gitignore
Below is one example of ignoring some files
```
*.mov
*.png
*.mp4
*.DS_Store
*.terraform
```

---

# Python and GenAI Gotchas

To run a notebook, I first created a python environment with a python runtime.
- Python version I selected: Python 3.12.6
- Since most of the code examples covered in Andrew's course use older version of openai, 
here are few additional steps to use the older version:
```bash
%%capture
!python -m pip install openai==0.27.0
!python -m pip install python-dotenv
```
---
### Approach in Harness to generate a sample maven hello-world project
```bash
export MAVEN_OPTS="-Xmx4g"
cd /genai
mvn org.apache.maven.plugins:maven-archetype-plugin:2.4:generate \
-DgroupId=com.organization.agentiveai \
-DartifactId=agentiveai \
-Dversion="0.1" \
-Dpackage=com.organization.agentiveai.code \
-DinteractiveMode=false
cd agentiveai
mvn package
java -cp target/agentiveai-0.1.jar com.organization.agentiveai.code.App
```

---

### How to know branches in remote origin?
```bash
git fetch
git branch -r
```

---

### How to trace a file in github 

- The below command will tell you the history of the file, what changed.
- Very useful in case you want to trace any deleted file which isn't locatable in github.
```bash
git log --follow -- A.java
```

---

### Git useful commands to know files that were modified in the commits
- git show --name-status <sha>
- git diff --name-only <sha>..HEAD
- git diff --name-only <sha1>..<sha2>