# Os pilares na árvore de arquivos: herança, polimorfismo, abstração e interface.
# Rodar no terminal: python3 pilares.py
#
# O Item da Aula 08 tinha um booleano (eh_pasta) e vários "if eh_pasta".
# Aqui ele vira três classes: Item (o geral), Pasta e Arquivo (os específicos),
# e quem usa a árvore deixa de perguntar "você é pasta?".
from abc import ABC, abstractmethod


# INTERFACE: contrato puro, sem estado e sem implementação.
# Quem assina promete saber dizer o próprio tamanho em bytes.
class Medivel(ABC):
    __slots__ = ()

    @abstractmethod
    def tamanho(self):
        pass


# ABSTRAÇÃO + HERANÇA: o que toda pasta e todo arquivo têm em comum.
# Não dá para criar um Item "solto": ele é só o recorte do essencial.
class Item(Medivel):
    __slots__ = ("__nome", "__pai")

    def __init__(self, nome, pai=None):
        self.__validar_nome(nome)
        self.__nome = nome
        self.__pai = None

        if pai is not None:
            self.mover_para(pai)

    def __validar_nome(self, nome):
        if nome == "" or "/" in nome:
            raise ValueError("nome inválido: " + repr(nome))

    @property
    def nome(self):
        return self.__nome

    @nome.setter
    def nome(self, novo_nome):
        self.__validar_nome(novo_nome)
        self.__nome = novo_nome

    @property
    def pai(self):
        return self.__pai

    def mover_para(self, destino):
        if destino is self.__pai:
            return

        destino._receber(self)
        if self.__pai is not None:
            self.__pai._soltar(self)
        self.__pai = destino

    # PROTEGIDO: o gancho que as filhas sobrescrevem. Por padrão, recusa.
    def _receber(self, item):
        raise ValueError(self.__nome + " é um arquivo, não pode conter itens")

    def caminho(self):
        if self.__pai is None:
            return self.__nome
        return self.__pai.caminho() + "/" + self.__nome

    def profundidade(self):
        if self.__pai is None:
            return 0
        return self.__pai.profundidade() + 1

    @abstractmethod
    def mostrar(self):
        pass


class Arquivo(Item):
    __slots__ = ("__bytes",)

    def __init__(self, nome, tamanho_bytes, pai=None):
        if tamanho_bytes < 0:
            raise ValueError("tamanho não pode ser negativo")
        self.__bytes = tamanho_bytes
        super().__init__(nome, pai)

    def tamanho(self):
        return self.__bytes

    def mostrar(self):
        recuo = "    " * self.profundidade()
        print(recuo + self.nome + " (" + str(self.tamanho()) + " B)")


class Atalho(Item):
    __slots__ = ("__destino",)

    # Um atalho é um item leve que aponta para outro item sem copiar seus dados.
    def __init__(self, nome, destino, pai=None):
        super().__init__(nome)
        self.__validar_destino(destino, pai)
        self.__destino = destino
        if pai is not None:
            self.mover_para(pai)

    # A propriedade deixa consultar o destino sem permitir troca direta.
    @property
    def destino(self):
        return self.__destino

    # O redirecionamento é a única forma pública de mudar o item apontado.
    def redirecionar(self, novo_destino):
        self.__validar_destino(novo_destino, self.pai)
        self.__destino = novo_destino

    # A validação também considera a pasta que será pai durante a construção.
    def __validar_destino(self, novo_destino, pai):
        if novo_destino is self:
            raise ValueError("um atalho não pode apontar para si mesmo")
        ancestral = pai
        while ancestral is not None:
            if novo_destino is ancestral:
                raise ValueError("um atalho não pode apontar para uma pasta que o contém")
            ancestral = ancestral.pai

    # O atalho ocupa sempre um byte, sem somar o tamanho do destino.
    def tamanho(self):
        return 1

    # A linha mostra o nome do atalho e o caminho do item apontado.
    def mostrar(self):
        recuo = "    " * self.profundidade()
        print(recuo + self.nome + " -> " + self.destino.caminho())


class Pasta(Item):
    __slots__ = ("__filhos",)

    def __init__(self, nome, pai=None):
        self.__filhos = []
        super().__init__(nome, pai)

    @property
    def filhos(self):
        return tuple(self.__filhos)

    # OVERRIDE do gancho protegido: a pasta aceita, desde que não crie um ciclo.
    def _receber(self, item):
        ancestral = self
        while ancestral is not None:
            if ancestral is item:
                raise ValueError("não dá para mover " + item.nome + " para dentro dela mesma")
            ancestral = ancestral.pai
        self.__filhos.append(item)

    def _soltar(self, item):
        self.__filhos.remove(item)

    # POLIMORFISMO: a pasta soma o que tem dentro; nenhum filho é perguntado
    # se é pasta ou arquivo, cada um responde do seu jeito.
    def tamanho(self):
        total = 0
        for filho in self.__filhos:
            total = total + filho.tamanho()
        return total

    def mostrar(self):
        recuo = "    " * self.profundidade()
        print(recuo + self.nome + "/ (" + str(self.tamanho()) + " B)")
        for filho in self.__filhos:
            filho.mostrar()


# Outra classe que assina o contrato SEM ser da árvore: a Lixeira.
class Lixeira(Medivel):
    __slots__ = ("__descartados",)

    def __init__(self):
        self.__descartados = []

    def descartar(self, arquivo):
        self.__descartados.append(arquivo)

    def tamanho(self):
        total = 0
        for arquivo in self.__descartados:
            total = total + arquivo.tamanho()
        return total


# Quem usa o contrato não sabe (nem quer saber) quem está do outro lado.
def espaco_total(coisas):
    total = 0
    for coisa in coisas:
        total = total + coisa.tamanho()
    return total


def tentar(rotulo, acao):
    try:
        acao()
        print(rotulo, "-> passou (!)")
    except Exception as erro:
        print(rotulo, "->", type(erro).__name__ + ":", erro)


disco = Pasta("C:")
usuarios = Pasta("Users", disco)
usuario = Pasta("klebe", usuarios)
desktop = Pasta("Desktop", usuario)
projetos = Pasta("Projetos", desktop)
relatorio = Arquivo("relatorio.txt", 120, desktop)
imagem = Arquivo("imagem.png", 2048, projetos)
atalho_arquivo = Atalho("atalho-relatorio", relatorio, desktop)
atalho_pasta = Atalho("atalho-projetos", projetos, desktop)
pasta_com_atalho = Pasta("PastaComAtalho", desktop)
arquivo_da_pasta = Arquivo("rascunho.txt", 50, desktop)
atalho_dentro_da_pasta = Atalho("atalho-interno", relatorio, pasta_com_atalho)

print("Árvore completa:")
disco.mostrar()

lixeira = Lixeira()
lixeira.descartar(Arquivo("descartado.txt", 30))
print("Espaço total:", espaco_total([arquivo_da_pasta, pasta_com_atalho, lixeira]), "B")

tentar(
    "Alterar destino pela propriedade",
    lambda: setattr(atalho_arquivo, "destino", imagem),
)
tentar(
    "Redirecionar atalho para si mesmo",
    lambda: atalho_arquivo.redirecionar(atalho_arquivo),
)
tentar(
    "Redirecionar atalho para a pasta que o contém",
    lambda: atalho_arquivo.redirecionar(desktop),
)
