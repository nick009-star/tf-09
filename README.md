Encapsulamento — interface: consultar `destino` e chamar `redirecionar()`; implementação: `__destino` fica privado e a troca valida destinos inválidos.
Herança — interface: o Atalho oferece `nome`, `pai`, `mover_para()` e `caminho()` como qualquer `Item`; implementação: esses dados e comportamentos são herdados, não duplicados.
Polimorfismo — interface: chamar `tamanho()` e `mostrar()` ou usar o `Atalho` em `espaco_total()` via `Medivel`; implementação: ele ocupa 1 byte e exibe o caminho do destino.
