# Architecture: a casca do projeto

> Autor: tech-lead · Modo: Definida (novo) / Mapeada (existente) · Status: Rascunho / Aprovada no F2 em <data>
> Em projeto novo, segue o Art. 8 da Constituição. Em projeto existente, descreve o que **é**, não o que deveria ser.

## Identidade
| Item | Valor |
|------|-------|
| applicationId / namespace base | `com.<empresa>.<app>` |
| minSdk / targetSdk / compileSdk | |
| Kotlin / AGP / Gradle | |
| Branch base | `develop` / `main` |

## Camadas e padrão de apresentação
- Clean Architecture: `presentation → domain ← data` (Art. 8.2)
- MVVM + MVI: `UiState` / `UiIntent` / `UiEffect` (Art. 8.3)
- Base de MVI compartilhada: <ex.: `MviViewModel<S, I, E>` em `:core:ui`, ou "nenhuma; cada ViewModel implementa o contrato">

## Mapa de módulos
| Módulo | Tipo (app / android-lib / jvm-lib) | Depende de | Responsabilidade |
|--------|------------------------------------|------------|------------------|
| :app | app | | |
| :core:designsystem | android-lib | | |
| :core:testing | android-lib | | |

## Convention plugins (`:build-logic`)
| Plugin | O que aplica |
|--------|--------------|
| `<app>.android.library` | |
| `<app>.android.feature` | |
| `<app>.jvm.library` | |

## Bibliotecas (version catalog)
| Área | Biblioteca | Versão |
|------|-----------|--------|
| | | |

## Convenções
- Pacotes: `<base>.feature.<nome>.{presentation,domain,data}`
- Nomes: `XxxRoute`, `XxxScreen`, `XxxViewModel`, `XxxUiState`, `XxxUiIntent`, `XxxUiEffect`, `GetXxxUseCase`, `XxxRepository` / `XxxRepositoryImpl`
- Erros: <como o domínio representa erro: `Result`, sealed class...>
- Navegação: <contratos de rota e onde ficam>

## Receita: como criar uma feature nova
1. Criar `:feature:<nome>:domain`, `:data` e `:presentation` com os convention plugins
2. ...

## Divergências do Art. 8 (só no modo mapeamento; informação, não defeito)
| O Art. 8 diz | O projeto faz | Impacto |
|--------------|---------------|---------|

## ADRs
- [0001: <título>](adr/0001-<titulo>.md)
