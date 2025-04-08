### Pre-req
- Install Github CLI 
- Check the status using : `gh auth status --hostname github.paypal.com`

It should return something like below: 

```bash
github.paypal.com
  ✓ Logged in to github.paypal.com account kkailasnath (keyring)
  - Active account: true
  - Git operations protocol: ssh
  - Token: gho_<secret>
  - Token scopes: 'admin:public_key', 'gist', 'read:org', 'repo'
```
If not, authenticate freshly using :

`gh auth login`, specify github.paypal.com , select defaults and SSH.

### Delete repo permission
- Use below command to request for delete_repo permission
- Without this, you can delete the repo.
- `gh auth refresh -h github.paypal.com -s delete_repo` 

### Use below to fetch list of repos in your name
- GH_HOST=github.paypal.com gh repo list --limit 10
- Since we now have two different githubs, one being github.paypal.com and other being github.com ( EMU instance), so we need to pass the GH_HOST as shown above( inline way).
- We could also export it as an environment variable using : 
    - `export GH_HOST=github.mycompany.com`

### List Archived Repos on Custom Domain
GH_HOST=github.paypal.com gh repo list --limit 1000 --json name,isArchived \
  -q '.[] | select(.isArchived==true) | .name'

### List Forked Repos on Custom Domain  
GH_HOST=github.paypal.com gh repo list --limit 1000 --json name,isFork \
  -q '.[] | select(.isFork==true) | .name'


