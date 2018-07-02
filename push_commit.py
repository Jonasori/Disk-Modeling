"""Stage, commit, and push a Git update."""


import subprocess as sp


s = sp.check_output(['git', 'status']).split('\n')
p = filter(None, s)

files = []
for i in p:
    if i[:1] == '\t':
        f = filter(None, i[1:].split(' '))[-1]
        files.append(f)

[sp.call(['git', 'stage', '{}'.format(i)]) for i in files]

commit_message = raw_input('Enter commit message:\n')

sp.call(['git', 'commit', '-m', '{}'.format(commit_message)])

sp.call(['git', 'push'])



# The End
