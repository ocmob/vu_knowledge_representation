# coding: utf-8
import pandas as pd
data = pd.read_csv('output.csv')
data
data.groupby('cmp_set').groupby('dimacs_set')
data.groupby(['cmp_set','dimacs_set'])
data.groupby(['cmp_set','dimacs_set']).mean()
get_ipython().run_line_magic('whos', '')
data_grouped = data.copy()
import re
data_grouped[re.search('randsat', data_grouped.dimacs_set)]
data_grouped.b.str.contains('^rand')
data_grouped.dimacs_set.str.contains('^rand')
data_grouped[data_grouped.dimacs_set.str.contains('^rand')] = rand
data_grouped[data_grouped.dimacs_set.str.contains('^rand')] = 'rand'
data_grouped[data_grouped.dimacs_set.str.contains('^1000')] = '1000'
data_grouped[data_grouped.dimacs_set.str.contains('^damn')] = 'damnhard'
data_grouped[data_grouped.dimacs_set.str.contains('^damn')]
data_grouped
data_grouped = data.copy()
data_grouped[data_grouped.dimacs_set.str.contains('^damn')].dimacs_set = 'damnhard'
data_grouped.loc[data_grouped.dimacs_set.str.contains('^damn')] = 'damnhard'
data_grouped.loc[data_grouped.dimacs_set.str.contains('^damn')]
data_grouped.loc[data_grouped.dimacs_set.str.contains('^damn')]
data_grouped = data.copy()
data_grouped
data_grouped.loc[data_grouped.dimacs_set.str.contains('^damn')].dimacs_set = 'damnhard'
data_grouped
data_grouped.loc[data_grouped.dimacs_set.str.contains('^damn')]['dimacs_set'] = 'damnhard'
data_grouped.loc[data_grouped.dimacs_set.str.contains('^damn')]
data_grouped.loc[data_grouped.dimacs_set.str.contains('^damn')].dimacs_set
data_grouped.loc[data_grouped.dimacs_set.str.contains('^damn')].dimacs_set = 'damn'
data_grouped.loc[data_grouped.dimacs_set.str.contains('^damn')].dimacs_set
data_grouped[data_grouped.dimacs_set.str.contains('^damn')].dimacs_set = 'damn'
data_grouped[data_grouped.dimacs_set.str.contains('^damn')]
data_grouped[data_grouped.dimacs_set.str.contains('^damn'), 'dimacs_set']
data_grouped[data_grouped.dimacs_set.str.contains('^damn')]['dimacs_set']
data_grouped[data_grouped.dimacs_set.str.contains('^damn')]['dimacs_set'] = 'damn;
data_grouped[data_grouped.dimacs_set.str.contains('^damn')]['dimacs_set'] = 'damn'
get_ipython().run_line_magic('whos', '')
data_grouped
data_grouped.SAT
data_grouped.SAT = 0
data_grouped.SAT
data_grouped.SAT = 1
data_grouped
data_grouped.dimacs_set
data_grouped.dimacs_set[data_grouped.dimacs_set.str.contains('^damn')]
data_grouped.dimacs_set[data_grouped.dimacs_set.str.contains('^damn')] = 'damn'
data_grouped
data_grouped.dimacs_set[data_grouped.dimacs_set.str.contains('^damn')] = 'damn'
data_grouped.dimacs_set[data_grouped.dimacs_set.str.contains('^1000')] = '1000'
data_grouped.dimacs_set[data_grouped.dimacs_set.str.contains('^rand')] = 'rand'
data_grouped
data_grouped.groupby(['cmp_set'])
data_grouped.groupby(['cmp_set']).mean()
data_grouped.groupby(['cmp_set','dimacs_set']).mean()
data.groupby('dimacs_set').mean()
data.groupby('cmp_set').mean().argmax()
data.groupby('cmp_set').mean().argmax().idxmax()
data.groupby('cmp_set').mean()..idxmax()
data.groupby('cmp_set').mean().idxmax()
data.groupby('cmp_set').mean()
data.groupby('cmp_set').mean().idxmax()
data.groupby('cmp_set').mean()
data_grouped.groupby(['cmp_set','dimacs_set']).mean()
data.groupby('cmp_set').mean()
get_ipython().run_line_magic('save', 'ipython_session.py')
get_ipython().run_line_magic('save', 'ipython_session')
