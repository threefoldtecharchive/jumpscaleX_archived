# Versioning
## Deciding the type of release
We use [semantic versioning](https://semver.org/), i.e. version labels have the form `v<major>.<minor>.<patch>`

* Patch release: `v0.8.1` to `v0.8.2`, only bug fixes
* Minor release: `v0.8.1` to `v0.9.0`, bug fixes and new features that maintain backwards compatibility
* Major release: `v0.8.1` to `v1.0.0`, bug fixes and new features that break backwards compatibility
 

# Branching strategy
The goal is to be able to hotfix the latest version in production
without impacting the development version.

We also need a way to version all our releases. The versionning should be consistent and understood by everyone.

We want to be able to let every developers to code freely on their feature branch without constantly syncing with the latest development.

We also want to make sure that all the code that is pushed to the repository have been reviewed to encourage collaboration and good practices.

We use the [gitflow](https://nvie.com/posts/a-successful-git-branching-model/) branching model. In short: since the last release, new features and bug fixes will have been merged into the develop branch through pull requests.


## Main branches
There is only two important branches that will live forever in the repository
* __master__
    * It reflects the version in production

* __development__
    * It reflects the next version that will be put in production

These branches are __protected__. It means that they require pull request reviews before merging.

## Supporting branches
Next to the main branches master and develop, we use a variety of supporting branches to aid parallel development between team members, ease tracking of features, prepare for production releases and to assist in quickly fixing live production problems.

Unlike the main branches, these branches always have a limited life time, since they will be removed eventually.

The different types of branches we may use are:

* Feature branches
* Release branches
* Hotfix branches

Each of these branches have a specific purpose and are bound to strict rules as to which branches may be their originating branch and which branches must be their merge targets. We will walk through them in a minute.



### Feature branches
When you have to develop a new feature or bug fix on the development branch

May branch off from:

`development`

Must merge back into:

`development`

Branch naming convention:

anything except `master`, `development`, `release-*`, or `hotfix-*`

### Release branches
Release branches support preparation of a new production release.  Furthermore, they allow for minor bug fixes and preparing meta-data for a release (version number, build dates, etc.). By doing all of this work on a release branch, the develop branch is cleared to receive features for the next big release.

May branch off from:

`develop`

Must merge back into:

`develop` __AND__ `master`

Branch naming convention:

`release-*`

### Hotfix branches
When a critical bug in a production version must be resolved immediately, a hotfix branch may be branched off from the corresponding tag on the master branch that marks the production version.

May branch off from:

`master`

Must merge back into:

`development` __AND__ `master`

Branch naming convention:

`hotfix-*`

to merge into `development` we can make a PR from `master` into `development` after the hotfix branch has been merged into `master`

### Action on a branch
Create a branch
```bash
$ git checkout -b myfeature development
Switched to a new branch "myfeature" based on develop
``` 

Rebasing a branch
```bash
$ git rebase development
will rebase your current branch on development
```

Tagging a branch 
 ```bash
$ git tag -a 1.2.1
```

Pushing to origin (especially after a rebase)
```bash
$ git push origin --force-with-lease
will push your branch on origin  your current branch on development
```

Git’s `push --force` is destructive because it unconditionally overwrites the remote repository with whatever you have locally, possibly overwriting any changes that a team member has pushed in the meantime. However there is a better way; the option –force-with-lease can help when you do need to do a forced push but still ensure you don’t overwrite other’s work.

#### Branch Clean-up

Using this workflow, you will end up with all kinds of redundant and abandoned supporting branches.
From time to time, you can clean them up with

```bash
$ git branch -d myBranchName_101026
``` 

or, if you haven’t ever merged the supporting branch (for example, if you just used it to prepare a patch
```bash
$ git branch -D comment_broken_links_101026
```

# Commit convention
When releasing a version or looking ath the git history we want all the commits to describe the changes in an uniform manner. That's why we need a convention.

## Format of the commit message

``` 
<type>(<scope>): <subject>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```
Any line of the commit message cannot be longer 100 characters! This allows the message to be easier to read on github as well as in various git tools.


### First line (Subject line)
Subject line contains succinct description of the change.

`Allowed <type>`

* feat (feature)
* fix (bug fix)
* docs (documentation)
* style (formatting, missing semi colons, …)
* refactor
* test (when adding missing tests)

`Allowed <scope>`
Scope could be anything specifying place of the commit change. For example wallet, nacl, bcdb, tfclient, etc...

`<subject> text`
use imperative, present tense: “change” not “changed” nor “changes”
don't capitalize first letter
no dot (.) at the end

### Message body
just as in use imperative, present tense: “change” not “changed” nor “changes”
includes motivation for the change and contrasts with previous behavior


### Message footer
#### Breaking changes
All breaking changes have to be mentioned in footer with the description of the change, justification and migration notes
```
BREAKING CHANGE: 3bot ssh key generation has changed.
    
    To migrate the code follow the example below:
    
    Before:
    
    j.nacl.create(words[])
    
    After:
    
    j.nacl.create("words")
    
    The array of words was not convenient enough to be used through the shell. We use a string with words separated by a whitespace instead.
```

#### Referencing issues
Closed bugs should be listed on a separate line in the footer prefixed with "Closes" keyword like this:
```
Closes #234
```
or in case of multiple issues:
```
Closes #123, #245, #992
```

## Examples
```
feat(clients): postgresql add exportToYAML

Added new method to  postgresql client:
- export all the database to the specified path

Breaks PostgresClient.queryToListDict, which was removed (use queryToList instead)

```

```
style(install): add couple of missing whitespaces
```

```
fix(builder): blockchain,  couple of unit tests for wallet generation

Some derivation path are not deep enough...
Would be better from a security point of view to use hardened key .

Closes #392
Breaks foo.bar api, foo.baz should be used instead
```

```
docs(guide): updated installation docs

Couple of typos fixed:
- indentation
- missing brace
New paragraph:
- docker on OSX
- antigravity in deep space
```
