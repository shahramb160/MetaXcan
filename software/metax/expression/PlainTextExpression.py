import re
import logging
import os
import gzip
import pandas
import Expression

########################################################################################################################
class ExpressionManager(Expression.ExpressionManager):
    def __init__(self, folder, pattern=None):
        gene_map, file_map = _structure(folder, pattern)
        self.gene_map = gene_map
        self.file_map = file_map
        self.d = None

    def expression_for_gene(self, gene):
        m_ = self.gene_map[gene]
        d = {model:self.d[model][gene].values for model in sorted(m_.keys())}
        return d

    def get_genes(self):
        return self.gene_map.keys()

    def enter(self):
        self.d = {name: pandas.read_table(path) for name, path in self.file_map.iteritems()}

    def exit(self):
        pass

class ExpressionManagerMemoryEfficient(Expression.ExpressionManager):
    def __init__(self, folder, pattern):
        gene_map, file_map = _structure(folder, pattern)
        self.gene_map = gene_map
        self.file_map = file_map

    def expression_for_gene(self, gene):
        m_ = self.gene_map[gene]
        k = {model:pandas.read_table(self.file_map[model], usecols=[gene])[gene].values for model in sorted(m_.keys())}
        return k

    def get_genes(self):
        return self.gene_map.keys()

_exregex = re.compile("TW_(.*)_0.5.expr.txt")
def _structure(folder, pattern=None):
    logging.info("Acquiring expression files")
    files = os.listdir(folder)
    gene_map = {}
    file_map = {}

    _regex = re.compile(pattern) if pattern else None

    for file in files:
        if _regex:
            if _regex.search(file):
                name = _regex.match(file).group(1)
            else:
                continue
        else:
            name = file
        name = name.replace("-", "_")
        path = os.path.join(folder, file)
        _o = gzip.open if ".gz" in file else open
        with _o(path) as f:
            comps = f.readline().strip().split()

            for i,gene in enumerate(comps):
                if not gene in gene_map:
                    gene_map[gene] = {}
                gene_map[gene][name] = i

            file_map[name] = path

    return gene_map, file_map

########################################################################################################################

class Expression(object):
    def __init__(self, path):
        self.path = path
        self.d = None

    def expression_for_gene(self, gene):
        k = self.d[gene].values
        return k

    def get_genes(self):
        return self.d.columns.values

    def enter(self):
        self.d = pandas.read_table(self.path)

    def exit(self):
        pass