# Spell Check!

This is used because I HATE reading American 

## How were words generated?
Outlining the creation of both British and American dictionaries.

### Creating dictionary

Install British-English dictionary (American-English is default)

```commandline
sudo apt install wbritish
# sudo apt install wbritish-large

# move to project folder (american-english for freedom enjoyers)
# or use british-english-large
cp ~/usr/share/dict/british-english ~/<directory>/british-english

# delete all words with apostrophes
ex -sc ':g/'\''/d' -c 'wq' british-english
```

