# Combination of synthetic graph generators # (first used in subgraph matching and motif mining)

import logging
import networkx as nx
import numpy as np

import deepsnap.dataset as dataset


class ERGeneratorEdgesCase(dataset.Generator):
    def __init__(self, sizes, p_alpha=1.3, shift_parameter = 1.0, **kwargs):
        super(ERGeneratorEdgesCase, self).__init__(sizes, **kwargs)
        self.p_alpha = p_alpha
        self.shift_parameter = shift_parameter

    def generate(self, size=None):
        num_nodes = self._get_size(size)
        # p follows beta distribution with mean = log2(num_graphs) / num_graphs
        alpha = self.p_alpha
        mean = (np.log2(num_nodes) / num_nodes) * self.shift_parameter
        if mean > 1.0:
            raise Exception("ERGenerator: shift parameter resulted in mean > 1.0")
        beta = alpha / mean - alpha
        p = np.random.beta(alpha, beta)
        graph = nx.gnp_random_graph(num_nodes, p)

        while not nx.is_connected(graph):
            p = np.random.beta(alpha, beta)
            graph = nx.gnp_random_graph(num_nodes, p)
        logging.debug('Generated {}-node E-R graphs with average p: {}'.format(
            num_nodes, mean))
        return graph

class ERGeneratorNodesCase(dataset.Generator):
    def __init__(self, sizes, p_alpha=1.3, shift_parameter = 1.0, **kwargs):
        if len(sizes)!= 1:
            raise Exception("Max wants an exception here. Sizes contains more than 1 element.")
        original_number_of_nodes = sizes[0]
        sizes = [round(element * shift_parameter) for element in sizes]
        super(ERGeneratorNodesCase, self).__init__(sizes, **kwargs)
        self.p_alpha = p_alpha
        self.shift_parameter = shift_parameter
        self.edge_rescale = (original_number_of_nodes-1)/(shift_parameter*(shift_parameter*original_number_of_nodes-1))

    def generate(self, size=None):
        num_nodes = self._get_size(size)
        # p follows beta distribution with mean = log2(num_graphs) / num_graphs
        alpha = self.p_alpha
        mean = (np.log2(num_nodes) / num_nodes) * self.edge_rescale
        if mean > 1.0:
            raise Exception("ERGenerator: shift parameter resulted in mean > 1.0")
        beta = alpha / mean - alpha
        p = np.random.beta(alpha, beta)
        graph = nx.gnp_random_graph(num_nodes, p)

        while not nx.is_connected(graph):
            p = np.random.beta(alpha, beta)
            graph = nx.gnp_random_graph(num_nodes, p)
        logging.debug('Generated {}-node E-R graphs with average p: {}'.format(
            num_nodes, mean))
        return graph


class WSGeneratorEccentricityCase(dataset.Generator):
    def __init__(self, sizes, density_alpha=1.3,
                 rewire_alpha=2, rewire_beta=2, shift_parameter = 1.0, **kwargs):
        super(WSGeneratorEccentricityCase, self).__init__(sizes, **kwargs)
        self.density_alpha = density_alpha
        self.rewire_alpha = rewire_alpha
        self.rewire_beta = rewire_beta
        self.shift_parameter = shift_parameter

    def generate(self, size=None):
        num_nodes = self._get_size(size)
        curr_num_graphs = 0

        density_alpha = self.density_alpha
        density_mean = (np.log2(num_nodes) / num_nodes) * self.shift_parameter
        if density_mean > 1.0:
            raise Exception("WSGenerator: shift parameter resulted in mean > 1.0")
        density_beta = density_alpha / density_mean - density_alpha
        rewire_alpha = self.rewire_alpha
        rewire_beta = self.rewire_beta
        while curr_num_graphs < 1:
            k = int(np.random.beta(density_alpha, density_beta) * num_nodes)
            k = max(k, 2)
            p = np.random.beta(rewire_alpha, rewire_beta)
            try:
                graph = nx.connected_watts_strogatz_graph(num_nodes, k, p)
                curr_num_graphs += 1
            except:
                pass
        logging.debug('Generated {}-node W-S graph with average density: {}'.format(
            num_nodes, density_mean))
        return graph


class BAGenerator(dataset.Generator):
    def __init__(self, sizes, max_p=0.2, max_q=0.2, **kwargs):
        super(BAGenerator, self).__init__(sizes, **kwargs)
        self.max_p = 0.2
        self.max_q = 0.2

    def generate(self, size=None):
        num_nodes = self._get_size(size)
        max_m = int(2 * np.log2(num_nodes))
        found = False
        m = np.random.choice(max_m) + 1
        p = np.min([np.random.exponential(20), self.max_p])
        q = np.min([np.random.exponential(20), self.max_q])
        while not found:
            graph = nx.extended_barabasi_albert_graph(num_nodes, m, p, q)
            if nx.is_connected(graph):
                found = True
        logging.debug('Generated {}-node extended B-A graph with max m: {}'.format(
            num_nodes, max_m))
        return graph


class PowerLawClusterGenerator(dataset.Generator):
    def __init__(self, sizes, max_triangle_prob=0.5, **kwargs):
        super(PowerLawClusterGenerator, self).__init__(sizes, **kwargs)
        self.max_triangle_prob = max_triangle_prob

    def generate(self, size=None):
        num_nodes = self._get_size(size)
        max_m = int(2 * np.log2(num_nodes))
        m = np.random.choice(max_m) + 1
        p = np.random.uniform(high=self.max_triangle_prob)
        found = False
        while not found:
            graph = nx.powerlaw_cluster_graph(num_nodes, m, p)
            if nx.is_connected(graph):
                found = True
        logging.debug('Generated {}-node powerlaw cluster graph with max m: {}'.format(
            num_nodes, max_m))
        return graph


def get_generator(sizes, size_prob=None, dataset_len=None):
    #gen_prob = [1/3.5, 1/3.5, 1/3.5, 0.5/3.5]
    generator = dataset.EnsembleGenerator(
        [ERGenerator(sizes, size_prob=size_prob),
            WSGenerator(sizes, size_prob=size_prob),
            BAGenerator(sizes, size_prob=size_prob),
            PowerLawClusterGenerator(sizes, size_prob=size_prob)],
        # gen_prob=gen_prob,
        dataset_len=dataset_len)
    # print(generator)
    return generator

def get_ERgeneratorNodes(sizes, size_prob=None, dataset_len=None, shift_parameter=None):
    #gen_prob = [1/3.5, 1/3.5, 1/3.5, 0.5/3.5]
    generator = dataset.EnsembleGenerator(
        [ERGeneratorNodesCase(sizes, size_prob=size_prob, shift_parameter=shift_parameter)],
        # gen_prob=gen_prob,
        dataset_len=dataset_len)
    # print(generator)
    return generator

def get_ERgeneratorEdges(sizes, size_prob=None, dataset_len=None, shift_parameter=None):
    #gen_prob = [1/3.5, 1/3.5, 1/3.5, 0.5/3.5]
    generator = dataset.EnsembleGenerator(
        [ERGeneratorEdgesCase(sizes, size_prob=size_prob, shift_parameter=shift_parameter)],
        # gen_prob=gen_prob,
        dataset_len=dataset_len)
    # print(generator)
    return generator

def get_WSgeneratorEccentricity(sizes, size_prob=None, dataset_len=None, shift_parameter=None):
    #gen_prob = [1/3.5, 1/3.5, 1/3.5, 0.5/3.5]
    generator = dataset.EnsembleGenerator(
        [WSGeneratorEccentricityCase(sizes, size_prob=size_prob, shift_parameter=shift_parameter)],
        # gen_prob=gen_prob,
        dataset_len=dataset_len)
    # print(generator)
    return generator

def get_dataset(task, dataset_len, sizes, generatorName="ERNODES", size_prob=None, shift_parameter=1.0, **kwargs):
    if generatorName == "ERNODES":
        generator = get_ERgeneratorNodes(sizes, size_prob=size_prob,
                                  dataset_len=dataset_len, shift_parameter=shift_parameter)
    if generatorName == "EREDGES":
        generator = get_ERgeneratorEdges(sizes, size_prob=size_prob,
                                  dataset_len=dataset_len, shift_parameter=shift_parameter)
    if generatorName == "WSECCENTRICITY":
        generator = get_WSgeneratorEccentricity(sizes, size_prob=size_prob,
                                  dataset_len=dataset_len, shift_parameter=shift_parameter)
    return dataset.GraphDataset(
        None, task=task, generator=generator, **kwargs)


def main():
    sizes = np.arange(6, 31)
    dataset = get_dataset("graph", sizes)
    print('On the fly generated dataset has length: {}'.format(len(dataset)))
    example_graph = dataset[0]
    print('Example graph: nodes {}; edges {}'.format(
        example_graph.G.nodes, example_graph.G.edges))

    print('Even the same index causes a new graph to be generated: edges {}'.format(
        dataset[0].G.edges))

    print('This generator has no label: {}, '
          '(but can be augmented via apply_transform)'.format(dataset.num_node_labels))


if __name__ == '__main__':
    main()
