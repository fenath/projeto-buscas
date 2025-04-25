from __future__ import annotations
from typing import Callable, override
from mapa import BELEZAS, MAPA, FRONTEIRAS, CUSTOS, get_uf_by_cidade, get_cidade_by_uf, get_distancia_aerea

DESTINO_NAO_ENCONTRADO: tuple[list[Node], int] = ([], 0)

class Node():
    def __init__(self, _name: str):
        self.name: str = _name
        self.connections: list[tuple[Node, int]] = []

    def add_connection(self, conn_name: str, cost: int) -> Node:
        conn = self.get_connection_by_name(conn_name)
        if conn:
            # Conexão ja existe
            return conn
            
        conn = Node(conn_name)
        
        self.add_connection_node(conn, cost)
        conn.add_connection_node(self, cost)
        return conn
        
    def add_connection_node(self, conn_node: Node, cost: int) -> None:
        if conn_node in self.get_children():
            return
        self.connections.append((conn_node, cost))
        
    def get_connection_by_name(self, conn_name: str)\
             -> Node | None:
        result = filter(lambda n: n[0].name == conn_name, self.connections)
        result = next(result, None)
        if result:
            return result[0]
        return None
    
    def get_children(self) -> list[Node]:
        return [conn[0] for conn in self.connections]
        
    def get_costs(self) -> list[int]:
        return [conn[1] for conn in self.connections]

    def get_cost(self, conn: Node) -> int | None:
        result = filter(lambda n: n[0] == conn, self.connections)
        result = next(result, None)
        if result:
            return result[1]
        return None

    def get_connection_cost(self, conn_name: str) -> int | None:
        result = filter(lambda n: n[0].name == conn_name, self.connections)
        result = next(result, None)
        if result:
            return result[1]
        return None

    @override
    def __repr__(self) -> str:
        return f'Node({self.name})'

    @override
    def __str__(self) -> str:
        return f'Node({self.name})'

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

def g_func(rota: list[Node]) -> int:
    custo = 0
    for i in range(len(rota) - 1):
        c = rota[i].get_cost(rota[i + 1])
        if c:
            custo += c
    return custo

def get_beleza(capital: Node) -> int:
    linha = list(filter(lambda n: n[0] == capital.name, (l for l in MAPA)))
    uf: str = linha[0][2] 
    beleza = BELEZAS[uf]
    return beleza

def h_func_beleza(trajeto: list[Node], destino: Node) -> int:
    """Heurística: penaliza caminhos que passam por cidades menos belas"""
    if not trajeto:
        return 0
    ultima = trajeto[-1]
    return 10 - get_beleza(ultima)  # Quanto mais bela, menor a heurística

def h_func_distancia_aerea(trajeto: list[Node], destino: Node) -> int:
    if not trajeto: 
        return 0

    ultima = trajeto[-1]

    uf_destino = str(get_uf_by_cidade(destino.name))
    uf_ultima = str(get_uf_by_cidade(ultima.name))

    cust = int(get_distancia_aerea(uf_ultima, uf_destino))
    return cust


def a_star(_mapa: list[Node], source: Node, dest: Node, h_func: Callable[[list[Node], Node], int] = h_func_beleza) -> tuple[list[Node], int]:
    """
    Busca usando método A*
    retorna o trajeto (se houver) e o custo para o trajeto

    - source: nó de origem
    - dest: nó de destino
    - mapa: lista de nós 
        (dá para perceber que acabamos não usando o mapa porque os próprios 
        nodes já possuem conexões)
    """

    # armazenar os próximos a fazer consulta
    next_children: list[tuple[Node, list[Node]]] = []
    visitados: set[Node] = set() # Usando set pois não armazena duplicados

    # Populando primeiro
    next_children.append((source, []))

    while next_children:
        def soma_g_h_func(key: tuple[Node, list[Node]]) -> int:
            # g(n) + h(n)
            _atual, trajeto = key
            return g_func(trajeto) + h_func(trajeto + [_atual], dest)

        # Ordena pela soma do custo atual e heurística
        next_children.sort(key=soma_g_h_func)
        proximos_5 = next_children[:5]
        #print('Proximos:')
        #print('\n'.join([f'{soma_g_h_func(n):3} - {n[0].name}' for n in proximos_5]))

        # Pega o nó com menor custo total estimado
        child, trajeto = next_children.pop(0)

        if child in visitados:
            continue

        visitados.add(child)
        rota_atual = trajeto + [child]
        if child == dest:
            # chegou no destino
            return rota_atual, g_func(rota_atual)

        children = child.get_children()
        # Adiciona filhos ao fim da lista
        next_children += [(conn, rota_atual) for conn in children]

    # Se não achou o destino
    return DESTINO_NAO_ENCONTRADO

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
    # print(f'Algoritmo de largura de {source.name} para {dest.name}')
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
            custo = g_func(rota_atual)
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
    
    return DESTINO_NAO_ENCONTRADO
        
    
def profundidade(_mapa: list[Node], source: Node, dest: Node) -> tuple[list[Node], int]:
    """
    Busca em profundidade
    retorna o trajeto (se houver) e o custo para o trajeto

    - source: nó de origem
    - dest: nó de destino
    - mapa: lista de nós 
    """
    print(f'Algoritmo de profundidade de {source.name} para {dest.name}')
    next_children: list[tuple[Node, list[Node]]] = []
    visitados: list[Node] = []

    next_children.append((source, []))

    while next_children:
        # Pega o último nó adicionado
        atual, trajeto = next_children.pop()

        if atual in visitados:
            continue

        visitados.append(atual)
        rota_atual = trajeto + [atual]

        if atual == dest:
            custo = g_func(rota_atual)
            return rota_atual, custo

        children = atual.get_children()

        # Como é pilha, adicionamos no final (últimos filhos serão explorados primeiro)
        next_children += [(filho, rota_atual) for filho in children if filho not in visitados]

    print('Destino não encontrado.')
    return DESTINO_NAO_ENCONTRADO


def get_cidade(mapa: list[Node], name: str) -> Node | None:
    linha = list(filter(lambda n: n.name == name, mapa))
    if not linha:
        return
    return linha[0]


def create_mapa() -> list[Node]:
    mapa: list[Node] = []

    def conectar_cidades(cidade1: Node, cidade2: Node, custo: int = 0) -> None:
        cidade1.add_connection_node(cidade2, custo)
        # Como cidades serao unidirecionais
        # cidade2.add_connection_node(cidade1)

    for linha in MAPA:
        cidade = Node(linha[0])
        mapa.append(cidade)

    def get_custos(uf: str) -> list[int]:
        return CUSTOS.get(uf, [])

    for cidade in mapa:
        uf = next(filter(lambda linha: linha[0] == cidade.name, MAPA))[2]
        capital = get_capital(uf)
        fronteiras = get_capitais_fronteiras(capital)
        custos = get_custos(uf)
        
        for front, custo in zip(fronteiras, custos):
            f_node = get_cidade(mapa, front)
            if f_node:
                conectar_cidades(cidade, f_node, custo)

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
    if trajeto:
        print(f'Viagem de {trajeto[0].name} a {trajeto[-1].name}')
    cidades_uf = [f'{n.name}({get_uf_by_cidade(n.name)})' for n in trajeto]
    print('Trajeto: {}'.format('->'.join(cidades_uf)))
    print('Custo: {}'.format(custo))
    return None

mapa = create_mapa()
capitais = [l[0] for l in MAPA]

def main() -> None:
    i = select_in('Origem', capitais)
    source = get_cidade(mapa, capitais[i])
    if not source:
        raise ValueError('Origem mal informada')

    i = select_in('Destino', capitais)
    dest = get_cidade(mapa, capitais[i])
    if not dest:
        raise ValueError('Destino mal informado')
    
    
    print('\n-----------------')
    print('Largura')
    print('-----------------')
    trajeto, custo = largura(mapa, source, dest)
    print_trajeto(trajeto, custo)
    print('-----------------')
    
    print('\n-----------------')
    print('Profundidade')
    trajeto, custo = profundidade(mapa, source, dest)
    print_trajeto(trajeto, custo)
    print('-----------------')
    
    print('\n-----------------')
    print('A Star')
    trajeto, custo = a_star(mapa, source, dest)
    print_trajeto(trajeto, custo)
    print('-----------------')

    print('\n-----------------')
    print('A Star (distancia aerea)')
    trajeto, custo = a_star(mapa, source, dest, h_func_distancia_aerea)
    print_trajeto(trajeto, custo)
    print('-----------------')

if __name__ == '__main__':
    main()
