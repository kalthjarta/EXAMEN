import VkApi
import pymorphy2, re
import networkx as nx, matplotlib.pyplot as plt
#networkx самое простое для построения графов, прогрессбар для красоты
import progressbar

morph = pymorphy2.MorphAnalyzer()
vk = VkApi.VkApi()
tokens = dict()


def tokenize(string, restriced_pos=['PREP', 'CONJ', 'PRCL', 'INTJ']):
    global tokens
    output = list()

    spl = string.split(' ')
    for word in spl:
        word = re.sub(r'\W', '', word.lower(), flags=re.UNICODE)
        p = morph.parse(word)[0]
        if p.tag.POS not in restriced_pos:
            if word in tokens:
                token = tokens[word]
            else:
                token = len(tokens)
                tokens[word] = token
            output.append(token)
    return output


def get_connections(source, max_posts=-1):
    global vk
    connections = list()  # [(tok1, tok2, weight), ]

    posts = vk.get_posts(source, max_posts)
    for r_p in posts:
        pbar = progressbar.ProgressBar()
        for post in pbar(r_p['response']['items']):
            # post_id = post['id']
            post_text = post['text']
            post_tokens = tokenize(post_text)

            i = 0; max = len(post_tokens) - 1
            while i < max:
                t1 = post_tokens[i]
                t2 = post_tokens[i+1]
                f = False
                for j, c in enumerate(connections):
                    if (c[0] == t1 and c[1] == t2) or (c[0] == t2 and c[1] == t1):
                        connections[j] = (c[0], c[1], c[2]+1)
                        f = True
                        break
                if not f:
                    connections.append((t1, t2, 1))
                i += 1
    return connections


def create_gexf(connections, filename):
    G = nx.Graph()
    G.add_weighted_edges_from(connections)
    for node in G.nodes_iter():
        G.node[node]['label'] = int(node)
    nx.write_gexf(G, filename)


def draw_gexf(filename, pngout_filename, figsize):
    G = nx.read_gexf(filename)
    pos = nx.spring_layout(G)
    labels = dict()
    for node in G.nodes_iter():
        labels[node] = list(tokens.keys())[list(tokens.values()).index(int(G.node[node]['label']))]
    plt.figure(1, (figsize, figsize))
    nx.draw_networkx(
        G,
        pos=pos,
        nodelist=G.nodes(),
        labels=labels,
        node_color='#CCCCCC',
        edge_color='#507299',
        font_size=8
    )
    elabels = dict(
        map(lambda x: ((x[0], x[1]), str(x[2]['weight'] if x[2]['weight'] <= 3 else "")), G.edges(data=True)))
    nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=elabels)
    plt.axis('off')
    plt.savefig(pngout_filename)


def write_gexf_info(filename, txtout_filename):
    G = nx.read_gexf(filename)
    with open(txtout_filename, 'w') as f:
        f.writelines([
            "Nodes: %i\n" % G.number_of_nodes(),
            "Edges: %i\n" % G.number_of_edges(),
            "Density: %f\n" % nx.density(G)
        ])


connections = get_connections('inrussiacom', 50)
create_gexf(connections, 'graph.gexf')
draw_gexf('graph.gexf', 'graph.png', 30)
write_gexf_info('graph.gexf', 'graph_info.txt')
