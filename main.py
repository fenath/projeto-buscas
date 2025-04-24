from __future__ import annotations
from mapa import MAPA, FRONTEIRAS


class Node():
    def __init__(self, _name: str):
        self.name: str = _name
        self.connections: list[Node] = []
        self.costs: list[int] = []

    def add_connection(self, conn_name: str, cost: int) -> Node:
        conn = self.get_connection_by_name(conn_name)
        if conn:
            # Conexão ja existe
            return conn
            
        conn = Node(conn_name)
        
        self.add_connection_node(conn)
        self.add_cost(cost)
        conn.add_connection_node(self)
        conn.add_cost(cost)
        return conn
        
    def add_connection_node(self, conn_node: Node):
        if conn_node in self.get_children():
            return
        self.connections.append(conn_node)
        
    def add_cost(self, cost: int):
        self.costs.append(cost)
    
    def get_connection_by_name(self, conn_name: str)\
             -> Node | None:
        result = filter(lambda n: n.name == conn_name, self.connections)
        return next(result, None)
    
    def get_children(self) -> list[Node]:
        return self.connections
        
    def get_costs(self) -> list[int]:
        return self.costs
        

def get_capital(uf: str) -> str:
    linha = list(filter(lambda n: n[2] == uf, (l for l in MAPA)))[0]
    if not linha:
        raise ValueError(f'UF {uf} não encontrada')
    return str(linha[0])

def get_fronteiras(uf: str) -> list[str]:
    if FRONTEIRAS.get(uf) is None:
        raise ValueError(f'UF {uf} não encontrada')
    return FRONTEIRAS.get(uf, [])

def get_capitais_fronteiras(capital: str) -> list[str]:
    linha = list(filter(lambda n: n[0] == capital, (l for l in MAPA)))
    uf: str = linha[0][2]
    fronteiras_uf = get_fronteiras(uf)
    capitais: list[str] = []
    for f in fronteiras_uf:
        capitais.append(get_capital(f))
    return capitais

def a_star(mapa: list[Node], source: Node, dest: Node):
    pass

def largura(_mapa: list[Node], source: Node, dest: Node) -> tuple[list[Node], int]:
    """
    Busca em largura 
    retorna o trajeto (se houver) e o custo para o trajeto

    - source: nó de origem
    - dest: nó de destino
    - mapa: lista de nós 
        (dá para perceber que acabamos não usando o mapa porque os próprios 
        nodes já possuem conexões)
    """
    print(f'Algoritmo de largura de {source.name} para {dest.name}')
    # Proximos filhos precisam armazenar a rota traçada
    next_children: list[tuple[Node, list[Node]]] = []
    visitados: list[Node] = []
    custo = 1

    # Popular o primeiro
    next_children.append((source, []))
    
    while next_children:
        child, trajeto = next_children.pop(0)
        # Nao voltar por um caminho ja feito
        if child in visitados:
            continue

        # print('TESTE: CITY: {} TRAJETO: {}'.format(
        #     child.name.ljust(15),
        #     '->'.join([t.name for t in trajeto]).ljust(100)
        # ))

        visitados.append(child)
        rota_atual = trajeto + [child]


        if child == dest:
            # chegou no destino
            custo = len(rota_atual)
            # print(f'Completou viagem de {source.name} a {dest.name}')
            # print(f'Trajeto: {[n.name for n in rota_atual]}')
            # print(f'Custo: {custo}')
            return rota_atual, custo
        
        children = child.get_children()
        # Adiciona filhos ao fim da lista
        # print('Adicionando {} filhos ({})'.format(
        #       len(children),
        #       str([s.name for s in children])
        #       ))
        next_children += [
            (conn, rota_atual) for conn in children
        ]
    
    return ([], 0) # Destino não encontrado
        
    
def profundidade(mapa: list[Node], source: Node, dest: Node):
    pass

def heuristica(mapa, source, dest): 
    pass

def get_cidade(mapa: list[Node], name: str) -> Node | None:
    linha = list(filter(lambda n: n.name == name, mapa))
    if not linha:
        return
    return linha[0]


def create_mapa() -> list[Node]:
    mapa: list[Node] = []

    def conectar_cidades(cidade1: Node, cidade2: Node) -> None:
        cidade1.add_connection_node(cidade2)
        # Como cidades serao unidirecionais
        # cidade2.add_connection_node(cidade1)

    for linha in MAPA:
        cidade = Node(linha[0])
        mapa.append(cidade)

    for cidade in mapa:
        uf = next(filter(lambda linha: linha[0] == cidade.name, MAPA))[2]
        capital = get_capital(uf)
        fronteiras = get_capitais_fronteiras(capital)
        for f in fronteiras:
            f_node = get_cidade(mapa, f)
            if f_node:
                conectar_cidades(cidade, f_node)

    return mapa

def select_in(msg: str, opcoes: list[str]) -> int:
    i = 0
    print(msg)
    while i < len(opcoes):
        op1 = opcoes[i]

        op2 = ''
        if i+1 < len(opcoes):
            op2 = opcoes[i + 1]

        print('{:2} - {} {:2} - {}'.format(i+1, op1.ljust(15), i+2, op2.ljust(15)))
        i += 2
    o = int(input('Insira opção: '))
    if o < 0:
        return 0
    if o > len(opcoes):
        return len(opcoes) - 1
    return o - 1

def print_trajeto(trajeto: list[Node], custo: int = 0) -> None:
    print(f'Viagem de {trajeto[0].name} a {trajeto[-1].name}')
    print('Trajeto: {}'.format('->'.join([n.name for n in trajeto])))
    print('Custo: {}'.format(custo))
    return None

def main() -> None:
    mapa = create_mapa()

    capitais = [l[0] for l in MAPA]
    i = select_in('Origem', capitais)
    source = get_cidade(mapa, capitais[i])
    if not source:
        raise ValueError('Origem mal informada')

    i = select_in('Destino', capitais)
    dest = get_cidade(mapa, capitais[i])
    if not dest:
        raise ValueError('Destino mal informado')
    
    
    print('-----------------')
    print('Largura')
    print('-----------------')

    trajeto, custo = largura(mapa, source, dest)
    print_trajeto(trajeto, custo)
    
    print('-----------------')
    print('Profundidade')
    print('-----------------')
    
    print('-----------------')
    print('Profundidade')
    print('-----------------')

if __name__ == '__main__':
    main()
