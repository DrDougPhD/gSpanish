import collections, itertools
VACANT_EDGE_ID = -1
VACANT_VERTEX_ID = -1
VACANT_EDGE_LABEL = -1
VACANT_VERTEX_LABEL = -1
VACANT_GRAPH_ID = -1
AUTO_EDGE_ID = -1

class Edge(object):
    def __init__(self, eid=VACANT_EDGE_ID,
                 frm=VACANT_VERTEX_ID,
                 to=VACANT_VERTEX_ID,
                 label=VACANT_EDGE_LABEL):
        self.eid = eid
        self.frm = frm
        self.to = to
        self.elb = self.label = label

class Vertex(object):
    def __init__(self, vid=VACANT_VERTEX_ID, label=VACANT_VERTEX_LABEL):
        self.vid = vid
        self.vlb = self.label = label
        self.edges = dict()

    def add_edge(self, eid, frm, to, elb):
        self.edges[to] = Edge(eid, frm, to, elb)


class Graph(object):
    def __init__(self, gid=VACANT_GRAPH_ID,
                       is_undirected=True,
                       eid_auto_increment=True):
        self.gid = gid
        self.is_undirected = is_undirected
        self.vertices = dict()
        self.edge_label_set = collections.defaultdict(set)
        self.vertex_label_set = collections.defaultdict(set)
        self.eid_auto_increment = eid_auto_increment
        self.counter = itertools.count()

    def get_num_vertices(self):
        return len(self.vertices)

    def add_vertex(self, vid, label):
        if vid in self.vertices:
            return self

        self.vertices[vid] = Vertex(vid, label)
        self.vertex_label_set[label].add(vid)
        return self

    def add_edge(self, eid, frm, to, edge_label):
        if frm in self.vertices\
           and to in self.vertices\
           and to in self.vertices[frm].edges:
               return self

        if self.eid_auto_increment:
            eid = self.counter.next()

        self.vertices[frm].add_edge(eid, frm, to, edge_label)
        self.edge_label_set[edge_label].add((frm, to))

        if self.is_undirected:
            self.vertices[to].add_edge(eid, to, frm, edge_label)
            self.edge_label_set[edge_label].add((to, frm))

        return self

    def remove_vertex(self, vid):
        if self.is_undirected:
            v = self.vertices[vid]
            for to in v.edges.keys():
                e = v.edges[to] # (vid, to) and (to, vid) have same elb
                self.edge_label_set[e.elb].discard((to, vid))
                del self.vertices[to].edges[vid]
        else:
            for frm in self.vertices.keys():
                v = self.vertices[frm]
                if vid in v.edges.keys():
                    e = self.vertices[frm].edges[vid]
                    self.edge_label_set[e.elb].discard((frm, vid))
                    del self.vertices[frm].edges[vid]

        v = self.vertices[vid]
        for to in v.edges.keys():
            e = v.edges[to]
            self.edge_label_set[e.elb].discard((vid, to))

        self.vertex_label_set[v.vlb].discard(vid)
        del self.vertices[vid]
        return self

    def remove_edge(self, frm, to):
        elb = self.vertices[frm].edges[to].elb
        self.edge_label_set[elb].discard((frm, to))
        del self.vertices[frm].edges[to]
        if self.is_undirected:
            self.edge_label_set[elb].discard((to, frm))
            del self.vertices[to].edges[frm]
        return self

    def remove_edge_with_elb(self, elb):
        for frm, to in list(self.edge_label_set[elb]): # use list. otherwise, 'Set changed size during iteration'
            self.remove_edge(frm, to)
        return self

    def remove_vertex_with_vlb(self, vlb):
        for vid in list(self.vertex_label_set[vlb]):
            self.remove_vertex(vid)
        return self

    def remove_edge_with_vevlb(self, vevlb):
        vlb1, elb, vlb2 = vevlb
        for frm, to in list(self.edge_label_set[elb]):
            if frm in self.vertex_label_set[vlb1] and to in self.vertex_label_set[vlb2]:
                self.remove_edge(frm, to)
        return self

    def display(self):
        print('t # {}'.format(self.gid))
        for vid in self.vertices:
            print('v {} {}'.format(vid, self.vertices[vid].vlb))
        for frm in self.vertices:
            edges = self.vertices[frm].edges
            for to in edges:
                if self.is_undirected:
                    if frm < to:
                        print('e {} {} {}'.format(frm, to, edges[to].elb))
                else:
                    print('e {} {} {}'.format(frm, to, edges[to].elb))

    def plot(self):
        try:
            import networkx as nx
            import matplotlib.pyplot as plt
        except Exception as e:
            print('Can not plot graph: {}'.format(e))
            raise

        gnx = nx.Graph() if self.is_undirected else nx.DiGraph()
        vlbs = {vid:v.vlb for vid, v in self.vertices.items()}
        elbs = {}
        for vid, v in self.vertices.items():
            gnx.add_node(vid, label = v.vlb)
        for vid, v in self.vertices.items():
            for to, e in v.edges.items():
                if (not self.is_undirected) or vid < to:
                    gnx.add_edge(vid, to, label = e.elb)
                    elbs[(vid, to)] = e.elb
        fsize = (min(16, 1 * len(self.vertices)), min(16, 1 * len(self.vertices)))
        plt.figure(3,figsize=fsize)
        pos = nx.spectral_layout(gnx)
        nx.draw_networkx(gnx, pos, arrows=True, with_labels=True, labels=vlbs)
        #nx.draw_networkx_labels(gnx,pos)
        nx.draw_networkx_edge_labels(gnx, pos, edge_labels=elbs)
        plt.show()
