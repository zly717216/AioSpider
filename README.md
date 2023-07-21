## License

This project is licensed under the terms of the MIT license. See the [LICENSE](LICENSE) file for details.

# AioSpider 开发文档（初稿）

让爬虫更简单，让爬虫更高效，让爬虫更智能

## 第一章 基本概况

### 1.1 AioSpider 简介

AioSpider框架：卓越且高效的协程异步爬虫解决方案

AioSpider是一款基于异步I/O (asyncio) 和aiohttp技术构建的高性能协程异步爬虫框架，专为大规模、高速和海量数据抓取任务而设计。这一先进的框架由多个功能丰富的组件组成，如系统引擎、request池、爬虫模块、下载器、解析器、中间件、ORM系统和数据管理器等，旨在为用户提供一流的数据抓取体验。

该框架具有诸多卓越特性，包括自由配置、自动调度、随机用户代理（UA）、自动代理、自动预警、数据自动入库、数据去重和断点续爬等功能。这些特性使得AioSpider能够在各种复杂环境中稳定运行，确保数据抓取过程既高效又可靠。

AioSpider致力于简化爬虫开发流程，提高开发效率，并降低JavaScript逆向工程的难度。为了实现这一目标，框架内集成了众多实用工具，以便开发者能够在更低成本下完成任务。此外，AioSpider还支持分布式集成，使得框架可以轻松地应对各种规模的数据抓取需求。

为了满足企业级用户的需求，AioSpider提供了远程企业微信自动化启动功能，实现了对数据和爬虫平台的远程管理。这一特性使得用户无需在本地启动爬虫，只需通过企业微信即可远程操控数据抓取任务，大幅度提高了工作效率。

总之，AioSpider框架凭借其高级、高效的特性，成为了大规模、高速和海量数据抓取任务的理想解决方案。它旨在简化爬虫开发流程，提高开发效率，帮助用户轻松应对各种复杂的数据抓取挑战。无论您是初学者还是经验丰富的开发者，AioSpider都将为您提供卓越的数据抓取体验。

### 1.2 AioSpider 特性

- 基于异步I/O (asyncio) 和aiohttp技术构建，性能高且稳定
- 支持 ORM 数据管理
- 具备自由配置、自动调度、随机 UA、自动代理、自动报警、自动入库、自动去重和断点续爬等功能
- 集成多种实用工具，降低开发难度和成本
- 支持分布式集成，适应不同规模的数据抓取需求
- 支持多平台预警
- 支持可视化数据平台管理
- 提供远程企业微信自动化功能，实现远程管理

### 1.3 AioSpider 安装指南

为了帮助您快速轻松地安装 AioSpider 框架，我们为您提供了如下详细的安装步骤。请按照以下指示逐步操作，确保安装过程顺利进行。

首先，请通过命令行界面执行以下命令，从 GitHub 仓库克隆 AioSpider 项目：

```bash
git clone https://github.com/zly717216/AioSpider.git
```

克隆完成后，进入AioSpider项目目录：

```bash
cd AioSpider
```

接下来，我们将使用pipenv工具来安装所需的依赖包。如果您尚未安装pipenv，请先执行`pip install pipenv`进行安装。然后运行以下命令：

```bash
pipenv install
```

完成依赖包安装后，激活pipenv虚拟环境：

```bash
pipenv shell
```

现在，您可以通过以下命令在虚拟环境中安装AioSpider：

```bash
pip install .
```

为了确保AioSpider已成功安装，请执行以下命令：

```bash
aioSpider -v
```

如果您看到了相应的版本信息，恭喜您！AioSpider 框架已成功安装在您的系统中。现在您可以开始使用 AioSpider 进行高效的数据抓取任务了。祝您使用愉快！

## 第二章 系统架构

### 2.1 架构设计

经过精心策划与设计，着重考虑了五个关键方面：设计理念、架构构思、用户体验与易用性、设计思路以及开发效率，以确保构建一个全面、高效且实用的异步爬虫框架。

#### 2.1.1 设计理念

AioSpider 框架的设计理念源于对高性能、高效率、易用性和可扩展性的追求。我们希望建立一个能够满足不同规模和复杂度数据抓取需求的解决方案，让开发者能够在简化开发流程的同时，提高开发效率和数据抓取速度。

#### 2.1.2 架构构思

AioSpider 采用了基于异步 I/O (asyncio) 和 aiohttp 技术的高性能协程异步爬虫框架。这种架构保证了在处理大规模、高速和海量数据抓取任务时，框架能够保持稳定和高效的性能表现。

AioSpider的架构构思主要包括以下几个方面：

1. 基于异步I/O (asyncio) 和aiohttp技术，确保框架在大规模数据抓取任务中的高效性能。
2. 模块化设计，将系统引擎、request池、爬虫模块、下载器、解析器、中间件、ORM系统和数据管理器等组件分离，提高可扩展性和可定制性。
3. 集成丰富的功能，如自动调度、随机用户代理（UA）、自动代理、自动预警、数据自动入库、数据去重和断点续爬等。
4. 提供简洁易用的API和丰富的文档，以便用户能够快速上手和应用。

#### 2.1.3 用户体验与易用性

AioSpider 致力于提供简单易用的用户体验。为了实现这一目标，我们集成了丰富的实用工具，降低了开发难度和成本。此外，我们还提供了详细的文档和示例，让用户能够快速上手并应对各种数据抓取挑战。

AioSpider 还支持分布式集成和远程管理，方便企业级用户进行数据抓取和爬虫平台管理。通过远程企业微信自动化启动功能，用户可以轻松地远程操控数据抓取任务，提高工作效率。

AioSpider框架注重用户体验与易用性。为实现这一目标，框架采取以下措施：

1. 提供简洁易用的API，帮助用户快速上手和应用。
2. 提供详尽的文档和示例教程，便于用户理解和掌握AioSpider的使用方法。
3. 设计灵活的配置选项，允许用户根据需求进行调整。

#### 2.1.4 设计思路

在设计 AioSpider 时，我们遵循了以下原则：

1. 保持简洁：减少不必要的功能和代码，专注于核心功能的实现。
2. 高性能：采用异步I/O和协程技术，确保在大规模数据抓取任务中保持高效稳定的性能。
3. 易扩展：设计灵活的架构，方便用户根据需求进行定制和扩展。
4. 高度模块化：将各个功能模块进行解耦，以实现更高的可维护性和可读性。
5. 用户友好：提供简洁易用的API和丰富的文档，让用户能够轻松上手和应用。

#### 2.1.5 开发效率

AioSpider 的设计旨在提高开发者的开发效率。通过以下几个方面实现这一目标：

1. 高性能：异步I/O和协程技术确保了AioSpider在大规模数据抓取任务中的高效性能，节省开发者的时间和资源。
2. 丰富的功能：提供自动调度、随机用户代理（UA）、自动代理、自动报警、数据自动入库、数据去重和断点续爬等功能，满足开发者在不同场景下的需求。
3. 灵活的架构：模块化设计使得AioSpider具有较高的可扩展性和可定制性，便于开发者根据自身需求进行修改和优化。
4. 详尽的文档和示例：提供全面的文档和实例教程，帮助开发者快速理解和掌握AioSpider的使用方法。
5. 社区支持：AioSpider持续完善并积极响应社区反馈，助力开发者解决遇到的问题。

综上，AioSpider框架凭借其高性能、易用性、可扩展性和高开发效率等特点，成为了数据抓取领域的理想解决方案。无论您是初学者还是经验丰富的开发者，AioSpider都将带给您高效、愉悦的开发体验。

### 2.2 工作流程

AioSpider框架是一款高性能的异步爬虫解决方案，其精心构建的模块使得数据抓取任务更加高效、便捷。以下是AioSpider框架的主要组成部分：

1. 系统引擎：作为框架的核心组件，系统引擎负责整个爬虫框架的运行和协调。它实现了任务的调度、请求的处理以及各个组件之间的通信和协作。系统引擎还负责加载配置文件，确保整个框架按照预定的配置运行。
2. 请求池：请求池是AioSpider框架中的关键组件，负责统一管理待处理的请求队列。它实现了请求调度、去重、优先级排序以及磁盘缓存和加载等功能。请求池的存在使得框架能够灵活地处理各种类型和数量的请求，提高了数据抓取的效率。
3. 爬虫模块：爬虫模块是框架中负责定义并实现数据抓取逻辑和策略的部分。开发者在爬虫模块中编写代码，指定目标网站、提取规则和数据处理方法。爬虫模块提供了丰富的API，使得开发者能够快速、简便地构建出功能强大的爬虫。
4. 下载器：下载器负责从目标网站获取页面资源。它可以处理HTTP、HTTPS和其他类型的请求，支持自定义请求头、随机用户代理（UA）和自动代理等功能。下载器还可以处理网络错误，确保数据抓取过程的稳定性。
5. 解析器：解析器为下载的页面资源提供解析接口，支持多种数据提取方法，如正则表达式、XPath、CSS选择器等。通过解析器，开发者可以轻松地从复杂的网页结构中提取有价值的信息。
6. 中间件：中间件在请求和响应的处理过程中发挥重要作用，允许开发者实现自定义扩展功能。例如，可以利用中间件实现请求和响应的拦截、修改，以满足特定场景下的需求。
7. ORM系统：ORM（对象关系映射）系统实现了数据库与清洗的数据之间的映射和持久化。它简化了数据存储和查询的操作，降低了开发者与数据库之间的沟通难度，提高了开发效率。
8. 数据管理器：数据管理器负责数据的存储、去重和整理。它可以将解析器提取出的数据保存到各种类型的数据库中，如MySQL、MongoDB、SQLite等。数据管理器还支持数据去重功能，避免在抓取过程中重复存储相同的信息。此外，数据管理器还可以对抓取到的数据进行整理和归类，方便开发者后续进行分析和处理。

综上所述，AioSpider框架通过以下模块精心构建，为开发者提供了一个高效、易用的协程异步爬虫解决方案：

- 系统引擎：负责框架的运行和协调
- 请求池：管理待处理请求队列，实现请求调度和去重
- 爬虫模块：定义并实现数据抓取逻辑和策略
- 下载器：从目标网站获取页面资源
- 解析器：提供解析接口，用于提取页面中的信息
- 中间件：处理请求和响应过程中的自定义扩展功能
- ORM系统：实现数据库与清洗数据之间的映射和持久化
- 数据管理器：负责数据的存储、去重和整理

通过这些模块的协同工作，AioSpider框架能够为开发者提供一个高级、高效的数据抓取解决方案。它旨在简化爬虫开发流程，提高开发效率，帮助用户轻松应对各种复杂的数据抓取挑战。无论您是初学者还是经验丰富的开发者，AioSpider都将为您提供卓越的数据抓取体验。

架构设计图如下：

![AioSpider架构图](D:\AioSpider\assets\AioSpider架构图.png)

AioSpider的工作流程如下：

1. 爬虫启动，并激活系统引擎。
2. 引擎加载配置文件，对各个模块进行初始化与配置，并负责整个框架的运行和协调。
3. 执行爬虫模块的`start_requests`方法，生成初始请求对象，以便开始数据抓取任务。
4. 初始请求经过爬虫中间件处理，添加自定义逻辑后，被引擎推送至请求池的`waiting`队列。
5. 请求池对`waiting`队列中的请求进行优先级调度和处理，将其移至`pending`队列。
6. 引擎从请求池的`pending`队列中获取请求，并将其交付给下载器，开始下载页面资源。
7. 下载器将请求传递给下载中间件，实现自定义处理逻辑，再从网络端获取响应。
8. 响应经过下载中间件处理后，返回至下载器，随后回到引擎进行后续处理。
9. 引擎判断请求是否成功。若失败，则将请求放入`failure`队列；若成功，则将请求放入 `url_db`队列。
10. 将成功的请求交给爬虫模块的对应回调函数进行解析，提取所需数据。
11. 解析后，若返回Model对象，则引擎将数据提交给数据管理器进行存储和去重处理。若返回请求对象，则再次执行上述工作流程。
12. 当请求池的`waiting`、`pending`和`failure`队列全部清空时，爬虫任务顺利结束。

### 2.3 核心组件

#### 2.3.1 引擎

##### 简介

ASpider引擎是一个基于Python的异步网络爬虫框架。它旨在帮助开发者轻松地构建高效、可扩展和易于维护的网络爬虫。AioSpider引擎的主要特点包括：使用异步I/O操作提高性能，支持中间件和扩展，以及提供一套完整的数据处理流程。

##### 设计思路

AioSpider引擎的设计核心是基于事件循环和异步编程。事件循环是AioSpider引擎的心脏，它负责调度各种任务并确保它们能够同时运行。异步编程允许AioSpider引擎在等待网络I/O操作完成的同时执行其他任务，从而实现高性能的并发处理。

##### 引擎的功能和作用

AioSpider引擎主要实现了以下功能：

- 请求处理：通过异步I/O和事件循环实现高效的请求处理。
- 中间件支持：允许开发者为请求和响应处理过程添加自定义逻辑。
- 数据处理：将解析后的数据存储到指定的数据源，支持多种数据模型。
- 设置管理：提供灵活的配置选项，以便根据项目需求定制爬虫行为。
- 日志记录：通过日志系统记录爬虫运行过程中的关键信息，便于调试和监控。

#### 2.3.2 Request 池

##### 简介

Request池（请求池）是一个数据结构，用于存储和管理即将被执行的网络请求（如HTTP请求）。在爬虫或网络应用中，请求池对于实现请求的优先级、调度和限制访问速率等功能至关重要。它允许您有序地处理和管理多个请求，以便根据不同的规则和约束（如优先级、域名等）高效地执行请求。

##### 组成

Request池在AioSpider框架中起着关键的作用，它负责请求的调度、去重、磁盘缓存与加载以及分布式队列的管理。它由四个主要队列组成，包括`waiting`、`pending`、`failure`队列以及`done`队列。接下来，我们将详细介绍这些队列及其功能。

1. `waiting`队列：此队列存储待发起的Request对象。当引擎将请求推送至此队列时，Request池会对请求进行去重判断，以确保不重复抓取相同的URL。此外，Request池还会检查请求是否已被抓取过，从而避免不必要的重复工作。为了提高效率，Request池会根据请求优先级对`waiting`队列进行排序，确保优先级较高的请求能够被优先处理。
2. `pending`队列：此队列存储正在进行的Request对象。当请求通过`waiting`队列的筛选后，它们将被放入`pending`队列，等待引擎处理。引擎从`pending`队列中获取请求并将其传递给下载器，进行页面资源的下载。为了防止队列阻塞，Request池会根据系统资源和网络状况动态调整`pending`队列中请求的处理速度。
3. `failure`队列：此队列存储处理失败的Request对象。当引擎无法成功处理某个请求时，它会将该请求放入`failure`队列。Request池将定期检查此队列，对失败的请求进行重试或诊断。此外，Request池还可以根据配置文件自动报警，通知开发者关注可能存在的问题。
4. `done`队列：此队列存储已完成的Request对象。当引擎成功处理请求后，它会将请求放入`done`队列，以记录已完成的抓取任务。Request池会将此队列中的数据持久化至磁盘，确保在程序意外终止时不丢失已完成的请求记录。

Request池设计图如下：

![Request池](D:\AioSpider\assets\Request池.png)

Request池的工作流程如下：

1. 引擎将请求推送至`waiting`队列，Request池对请求进行去重判断及检查是否已被抓取过。此外，根据请求优先级，Request池对`waiting`队列进行排序。
2. 请求经过处理后，进入`pending`队列，等待被引擎处理。Request池会根据系统资源和网络状况动态调整处理速度。
3. 引擎从`pending`队列中获取请求，进行后续处理。此过程包括将请求传递给下载器、下载页面资源、处理响应数据等。
4. 处理失败的请求将被引

#### 2.3.3 预加载器

AioSpider预加载器是AioSpider框架的一个重要组件，负责在框架启动时执行一些关键的初始化任务。预加载器通过加载配置、创建数据库连接、实例化浏览器和加载模型等操作，为框架的运行做好准备。本文档将详细介绍预加载器的设计思路、功能和作用，以帮助您更好地理解和使用AioSpider框架。

##### 简介

预加载器（Preloader）是一个负责在框架启动前执行一系列关键初始化任务的组件。这些任务包括加载配置文件、设置数据库连接、实例化浏览器以及加载模型等。预加载器的设计目的是为了确保AioSpider框架在启动时拥有正确的配置和所需的资源，从而保证框架能够顺利地运行。

##### 设计思路

预加载器的设计思路是将各个初始化任务分解为独立的模块，每个模块负责完成特定的任务。这种模块化设计使得预加载器的代码更容易理解和维护，也使得在未来需要添加新的初始化任务时可以更容易地扩展预加载器。

AioSpider预加载器包括以下模块：

1. `LoadSettings`：负责加载配置文件，并将配置信息保存到`GlobalConstant`中。
2. `LoadDatabase`：负责根据配置文件的设置，初始化和设置数据库连接。
3. `LoadBrowser`：负责根据配置文件的设置，实例化浏览器（如Chromium或Firefox）。
4. `LoadModels`：负责加载模型，并将模型信息保存到`GlobalConstant`中。

##### 功能和作用

1. 加载配置：预加载器的第一个任务是加载配置文件。配置文件包含了AioSpider框架运行所需的各种设置，如数据库连接信息、浏览器配置等。`LoadSettings`模块负责读取配置文件，并将配置信息保存到`GlobalConstant`中。这样，其他模块可以方便地访问这些配置信息，无需直接读取配置文件。
2. 设置数据库连接：预加载器的第二个任务是初始化和设置数据库连接。`LoadDatabase`模块负责根据配置文件的设置，创建数据库连接。这包括初始化SQLite、CSV、MySQL和MongoDB等不同类型的数据库。将数据库连接保存到`GlobalConstant`中，可以确保在整个框架运行过程中，所有模块都能够方便地访问数据库。
3. 实例化浏览器：预加载器的第三个任务是实例化浏览器。`LoadBrowser`模块负责根据配置文件的设置，实例化浏览器（如Chromium或Firefox）。这使得AioSpider框架可以利用浏览器实例执行网页爬取、渲染和分析等任务。实例化浏览器时，预加载器会考虑各种配置选项，如是否启用无头模式、代理设置、用户代理设置等。浏览器实例将被保存到`GlobalConstant`中，以便在整个框架运行过程中方便地访问和使用。
4. 加载模型：预加载器的第四个任务是加载模型。`LoadModels`模块负责扫描并加载所有的数据模型。数据模型是AioSpider框架中非常重要的组件，用于描述和处理从爬取到的数据。通过在预加载阶段加载所有的数据模型，可以确保在框架运行过程中，所有模块都能够方便地访问和使用这些模型。加载的模型信息将被保存到`GlobalConstant`中。

##### 顺序、异常处理与扩展性

1. 预加载器的执行顺序：预加载器的执行顺序非常重要，因为各个模块之间可能存在依赖关系。例如，`LoadDatabase`和`LoadBrowser`模块都需要先加载配置信息。因此，预加载器应按照以下顺序执行模块：`LoadSettings` -> `LoadDatabase` -> `LoadBrowser` -> `LoadModels`。
2. 预加载器的异常处理：在预加载器执行过程中，可能会遇到各种异常，如配置文件错误、数据库连接失败等。为了确保框架能够正常运行，预加载器应当在遇到异常时提供详细的错误信息，并在某些情况下中止框架的启动。
3. 预加载器的可扩展性：预加载器采用模块化的设计思路，使得在未来需要添加新的初始化任务时可以更容易地扩展预加载器。当需要添加新的初始化任务时，可以创建一个新的模块，并在预加载器中按照适当的顺序执行该模块。

#### 2.3.4 下载器

AioSpider下载器的设计灵感来自于网络爬虫领域的实际需求和经验总结。下载器需要在不同场景下灵活、高效地处理各种网络请求，因此易于配置、高性能、稳定可靠和可扩展性成为其设计的核心理念。同时，我们借鉴了多种设计模式，如策略模式、工厂模式和单例模式，使得下载器的代码结构更加优雅、清晰，易于理解和维护。在这个过程中，我们汲取了众多优秀网络爬虫框架的设计理念，力求为用户提供一个功能强大、易于使用和扩展的网络抓取组件。

##### 简介

下载器（Downloader）是网络爬虫的一个关键组件，它负责将指定的URL请求并获取相应的网页数据。下载器作为爬虫的核心组成部分，实现了对特定网络资源的访问和抓取。在AioSpider框架中，下载器的实现提供了高度可配置、易于扩展的特性，可以满足不同场景和需求的网络抓取任务。

##### 设计思路

AioSpider下载器的设计理念主要体现在以下几个方面：

易于配置：下载器的设计旨在提供一个灵活、易于配置的网络抓取组件，以满足各种抓取需求。为了实现这一目标，我们提供了丰富的配置选项，如选择不同的网络请求库（aiohttp或requests），使用或不使用Session，以及调整连接数和连接池大小等。这使得下载器可以根据具体需求进行灵活地调整，以达到最佳的性能和稳定性。

高度可扩展：在设计下载器时，我们充分考虑了其可扩展性。下载器支持多种网络请求库，并且可以轻松地添加新的请求库以满足特定需求。同时，下载器的代码结构也易于扩展，例如使用工厂模式和策略模式，可以轻松地添加新的下载器实现或自定义下载器行为。

高性能：性能是下载器设计的核心考虑因素之一。我们采用了高效的异步网络库（如aiohttp）以及连接池技术，以确保下载器在高并发下的性能表现。此外，下载器还支持同步网络请求库（如requests），适用于低并发或简单的网络抓取任务。

稳定可靠：下载器的设计充分考虑了网络抓取过程中可能遇到的各种错误和异常。通过实现错误处理和异常捕获，下载器可以在遇到网络问题时继续稳定运行，而不会导致整个爬虫程序崩溃。此外，下载器还支持输入验证，以确保传递给下载器的参数是有效的，从而避免无效请求导致程序出现问题。

设计优雅：为了提高代码的可读性、可维护性和可拓展性，下载器在设计过程中采用了多种设计模式，如策略模式、工厂模式和单例模式。这些设计模式使得下载器的代码结构更加清晰，易于理解和维护。同时，这也为后续的功能扩展和优化提供了便利。

##### 设计模式

AioSpider下载器在设计和实现过程中使用了多种设计模式，使代码结构更加清晰、易于维护。主要包括以下几种设计模式：

1. 策略模式：通过定义一系列可互换的算法，使得算法可以独立于使用它的客户端而变化。在下载器中，我们将不同的网络请求库（aiohttp和requests）以及它们的同步和异步实现视为不同的策略。使用策略模式，可以轻松地切换不同的网络请求库和请求方式，以满足不同的需求。
2. 工厂模式：通过定义一个创建对象的接口，让子类决定实例化哪一个类。在下载器中，我们使用工厂模式来创建下载器实例。根据配置选项，工厂类负责创建适当的下载器实例。这样，我们可以轻松地扩展下载器，添加新的网络请求库或自定义下载器实现。
3. 单例模式：确保一个类只有一个实例，并提供一个全局访问点。在下载器中，我们使用单例模式来确保某些组件（如使用Session的网络请求库实例）只有一个实例。这样可以避免不必要的资源浪费，并确保组件在整个爬虫中共享。

##### 功能和作用

下载器的主要作用包括：

1. 向目标网站发送HTTP请求并获取响应数据。
2. 处理网络异常和错误，确保爬虫的健壮性。
3. 管理网络连接，包括连接数限制和连接池大小。
4. 支持多种网络请求库，如aiohttp和requests，以满足不同的抓取需求。

##### 多样化

AioSpider下载器支持多种网络请求库，包括aiohttp和requests。这些网络请求库具有各自的特点和优势，可以根据需求灵活选择。

- aiohttp：基于异步IO的高性能HTTP客户端库，适用于高并发的网络抓取任务。
- requests：简洁易用的同步HTTP客户端库，适用于低并发或简单的网络抓取任务。

下载器的多样化体现在：

1. 支持选择不同的网络请求库，以满足特定的抓取需求。
2. 提供了易于扩展的代码结构，可以轻松地添加新的请求库或自定义下载器实现。

#### 2.3.5 数据加载器

## 第三章 快速开始

### 3.1 命令行

#### 3.1.1 查看帮助

```bash
aioSpider -h
```

#### 3.1.2 查看版本

```bash
aioSpider -v
```

#### 3.1.3 创建项目

```bash
aioSpider create -p <project>
```

#### 3.1.4 创建爬虫

```bash
aioSpider create -s <spider>
```

#### 3.1.5 `sql` 表结构转 `model`

```bash
aioSpider make model -i <path>
```

#### 3.1.6 生成爬虫 `bat` 启动脚本

```bash
aioSpider make bat -o <path>
```

#### 3.1.7 启动 `aioSpider Server`

```bash
aioSpider server run -h <host> -p <port>
```

#### 3.1.8 停止 `aioSpider Server`

```bash
aioSpider server stop [-p <port>]
```

#### 3.1.9 测试 `IP` 带宽

```bash
aioSpider test proxy -p <proxy> --d <timeout>
```

### 3.2 使用步骤

（1）创建项目

```bash
aioSpider create -p myproject
```

（2）进入项目根路径

```bash
cd myproject
```



## 第四章 请求与响应

### 4.1 请求（Resquest）

#### 4.1.1 什么是请求

在AioSpider框架中，请求并非仅指典型的GET/POST方法，而是一个更为广义的概念。它包含了整个从爬虫模块开始，将请求参数封装成Request对象，到经过调度、去重、过滤和中间件处理，最后送达网络端的完整过程。换言之，当这样一个过程顺利完成，我们便认为AioSpider框架实现了一次请求。这种广义的请求概念，有助于更好地理解框架中各个组件之间的协同作用，以及它们在整个数据抓取过程中所发挥的关键作用。

#### 4.1.2 请求参数

AioSpider 中有两个请求类，分别是 Request 和 FormRequest，Request 用于发送 GET 请求，FormRequest 用于发送 POST 请求。	

Request 请求参数：

| 参数名      | 类型     | 默认值 | 注解              |
| ----------- | -------- | ------ | ----------------- |
| url         | str      | 无     | 网页请求 url 地址 |
| callback    | Callable | None   | 请求成功回调函数  |
| params      | dict     | None   | 请求参数          |
| headers     | dict     | None   | 请求头            |
| encoding    | str      | utf-8  | 响应解码编码      |
| cookies     | dict     | None   | 请求 cookies      |
| timeout     | int      | 0      | 请求超时时间      |
| proxy       | str      | None   | 请求代理          |
| priority    | int      | 1      | 请求优先级        |
| dnt_filter  | bool     | False  | 是否去重          |
| help        | str      | None   | 请求描述信息      |
| add_headers | dict     | None   | 添加请求头        |
| target      | str      | None   | 请求目标网址      |

FormRequest 请求参数：

| 参数名      | 类型      | 默认值 | 注解              |
| ----------- | --------- | ------ | ----------------- |
| url         | str       | 无     | 网页请求 url 地址 |
| callback    | Callable  | None   | 请求成功回调函数  |
| params      | dict      | None   | 请求参数          |
| headers     | dict      | None   | 请求头            |
| encoding    | str       | utf-8  | 响应解码编码      |
| data        | dict, str | None   | 请求体            |
| cookies     | dict      | None   | 请求 cookies      |
| timeout     | int       | 0      | 请求超时时间      |
| proxy       | str       | None   | 请求代理          |
| priority    | int       | 1      | 请求优先级        |
| dnt_filter  | bool      | False  | 是否去重          |
| help        | str       | None   | 请求描述信息      |
| add_headers | dict      | None   | 添加请求头        |
| target      | str       | None   | 请求目标网址      |

参数设计解释

- help 参数的设计初衷是：该参数是对请求信息的描述，主要是为了能够快速知道该请求是干嘛的；
- add_headers 参数的设计初衷是：该参数可以往拓展 headers 参数和 settings 中默认默认的请求头，主要是为了方便一些需要拓展请求头的特殊业务场景；
- target 参数的设计初衷是：该参数是对目标网址的标记，有些页面是动态的，该参数能够让人迅速知道该请求是在哪个页面看到的；

#### 4.1.3 如何构造请求

以构造东方财富行情请求实例为例：

```python
yield Request(
	url="http://push2his.eastmoney.com/api/qt/stock/kline/get",
    headers={
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Referer": "http://quote.eastmoney.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        			"Chrome/110.0.0.0 Safari/537.36"
    },
    params={
        "fields1": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
        "beg": "0",
        "end": "20500101",
        "ut": "fa5fd1943c7b386f172d6893dbfba10b",
        "rtntype": "6",
        "secid": "0.002789",
        "klt": "101",
        "fqt": "1",
        "cb": "jsonp1679996737236"
    },
    cookies={
        "qgqp_b_id": "8568daaa823378447451e28d5751b61b",
        "ct": "NexzX9yL-iRAg0KwwjU3RvnzDqkt3EW3ryenllRJcMUnTf8qysQ7orQ23xOD1RtqsacgG-OsuQ91RUYvfDg06fsemDqNUPRnbYQm14v3l3_fux5QYkmPCmRlwgOdjkiHUDIv8rgv1FTJ0KU6BHl6OCs2k2ZtBZRL6-BjWZ7-F0E",
        "ut": "FobyicMgeV6Gl5Ws0rOH5p7Xcgv448c0zNotm-Dv2RHx9OOxHRyDpKwiiEaTWyz37NUWP0hnKzq07jD6mi_oh8-WiuA2sdRT9OYs0jnv25VWEnDQWxMDLMm7VKh14mO1b-MSfvnW4q-pZeO60DyeORwvTGNCSW4vbgAhVzlSgAqz1nf8Y7KvSfIhZCE3UJ5Nep-oTGAo-X3J-Xm6-LHm7d958qA8rGSFX1INXrSlpSZ0KOJdh-KPCShOVz4H_Ye2we5zAU1KyX41FMbQZU9jpma3c4J4wNhi"
    },
    target='http://quote.eastmoney.com/concept/sz002789.html#fschart-r',
    help='东财日线'
)
```

在这个示例中，我们构建了一个针对东方财富行情的请求。

首先，我们定义了目标URL，然后设置了请求头信息，包括Accept、Accept-Language、Connection、Referer和User-Agent等字段。这些字段通常用于描述客户端和服务器之间的通信协议和约定。

接下来，我们添加了请求参数，包括股票代码、K线类型、复权类型等。这些参数是根据目标网站的API要求设置的。为了实现身份验证和状态保持，我们还提供了Cookie信息。

最后，我们为请求设置了目标页面和辅助信息，帮助我们更好地理解抓取到的数据。

在AioSpider框架中，构建请求的过程非常简洁且易于理解。用户只需要关注请求的URL、参数、头部信息以及Cookie等内容，而框架将负责处理请求的调度、去重、中间件处理等底层逻辑。这使得爬虫开发者可以专注于实现数据抓取逻辑，提高开发效率。

总之，AioSpider提供了一个灵活且高效的请求构建机制，使得开发者能够轻松地实现复杂的网页抓取任务。通过设置不同的请求参数、头部信息和Cookie等内容，用户可以针对不同的目标网站和场景构建合适的请求，从而满足各种数据抓取需求。

### 4.2 响应（Response）

#### 4.2.1 什么是响应

在AioSpider框架中，响应（Response）是指当一个请求（Request）经过网络端处理并返回数据后，框架将该数据封装为Response对象。响应对象包含了请求的结果信息，如HTTP状态码、响应头部信息、响应内容等。开发者可以根据这些信息判断请求是否成功，并从中提取所需的数据。

响应对象允许开发者在回调函数中对其进行解析，进一步提取目标数据。通过分析响应内容，用户可以定位所需信息的位置，使用解析器进行抽取，从而实现数据抓取任务的目标。

#### 4.2.3 响应参数

Response 类参数：

| 参数名  | 类型    | 默认值 | 注解                 |
| ------- | ------- | ------ | -------------------- |
| url     | str     | 无     | 目标请求 url 地址    |
| status  | int     | 200    | 响应状态码           |
| headers | dict    | None   | 响应头               |
| content | bytes   | b''    | 响应二进制流数据     |
| text    | str     | ''     | 响应字符串数据       |
| request | Request | None   | 该响应的请求实例对象 |

#### 4.2.3 响应属性和方法

| 名称    | 属性或方法 | 返回值类型 | 注解                                           |
| ------- | ---------- | ---------- | ---------------------------------------------- |
| url     | 属性       | str        | 目标请求 url 地址                              |
| status  | 属性       | int        | 响应状态码                                     |
| headers | 属性       | dict       | 响应头                                         |
| content | 属性       | bytes      | 响应二进制流数据                               |
| text    | 属性       | str        | 响应字符串数据                                 |
| request | 属性       | Request    | 该响应的请求实例对象                           |
| xpath   | 方法       | Parser     | xpath 数据提取方法                             |
| json    | 方法       | dict       | 解析 json 数据                                 |
| jsonp   | 方法       | dict       | 解析 jsonp 数据                                |
| eval_js | 方法       | Any        | 如果响应是js字符串，调用此方法可以执行 js 代码 |
| call_js | 方法       | Any        | 如果响应是js字符串，调用此方法可以调用 js 函数 |
| re      | 方法       | Parser     | 正则数据提取方法                               |

## 第五章 爬虫

### 5.1 普通爬虫

#### 5.1.1 简介

普通爬虫是AioSpider框架的基本爬虫类，用于一次性爬取数据并实现简单的网络爬取任务。与批次爬虫不同，它不涉及定时触发，适用于那些不需要定时执行的单次性爬取任务。通过普通爬虫，用户可以快速搭建爬虫功能，提取所需数据，并进行简单的数据处理。

#### 5.1.2 属性和方法

属性

- `name`: 爬虫的名称，用于标识爬虫实例。
- `source`: 爬虫的来源，可以用于记录爬虫爬取的网站来源等信息。
- `target`: 爬虫的目标，可以用于记录爬虫爬取的数据存储目标等信息。
- `description`: 爬虫的描述，用于简要说明爬虫的功能和特点。
- `version`: 爬虫的版本号，用于标识爬虫代码的版本信息。
- `start_urls`: 起始URL列表，用于指定爬虫开始爬取的入口URL。

方法

- `get_running_time(self)`: 获取爬虫的运行时间，返回格式为“时:分:秒”的字符串。
- `get_remaining_time(self)`: 获取爬虫剩余的运行时间，返回格式为“时:分:秒”的字符串。
- `spider_open(self)`: 爬虫启动时调用的方法，用于执行一些初始化操作。
- `spider_close(self)`: 爬虫关闭时调用的方法，用于执行一些清理操作。
- `start_requests(self)`: 构造起始请求，返回一个生成器对象，用于生成请求并调用解析回调函数。
- `parse(self, response)`: 解析回调函数，用于处理请求的响应数据。子类可以根据具体需求实现此方法。
- `default_parse(self, response: Response)`: 默认解析回调函数，可以由子类重写以定义通用的数据解析逻辑。

#### 5.1.3 使用

使用普通爬虫时，可以按照以下步骤进行：

1. 创建一个继承自Spider类的新爬虫类，根据实际需求在类中添加属性和方法。
2. 在新爬虫类中实现`start_requests`方法，指定爬虫的起始URL列表。
3. 在新爬虫类中实现`parse`方法，处理请求的响应数据，提取所需数据并进行处理。
4. 根据需要，在`__init__`方法中传入相应的参数，如登录用户名、密码、cookies等。
5. 启动引擎，导入爬虫实例或爬虫类，开始爬取数据。

以下是一个使用普通爬虫的示例代码：

```python
from AioSpider.spider import Spider
from AioSpider.http import Request


class MySpider(Spider):
    name = "my_spider"
    source = "http://example.com"
    target = "http://example.com/data"
    description = "This is a spider example."

    start_urls = ["http://example.com/data"]

    def parse(self, response):
        # 解析响应数据并提取所需信息
        data = response.json()
        # 处理数据的逻辑
        ...

        
if __name__ == "__main__":
    
    from AioSpider.core import Engine
    
    engine = Engine()
    engine.add_spider(MySpider)
    engine.start()
```

在以上示例中，我们分别创建了一个批次爬虫和一个普通爬虫。用户可以根据自己的需求来选择使用批次爬虫还是普通爬虫，实现定时爬取数据或单次爬取数据的功能。

总结起来，`AioSpider` 框架的爬虫类提供了一种高效、灵活且易于使用的方式来实现数据爬取任务。用户可以根据实际需求来选择不同类型的爬虫，并通过定制化的配置和扩展来满足复杂的爬取需求。这使得 `AioSpider` 成为一个强大的工具，适用于各种数据爬取场景。

### 5.2 批次爬虫

#### 5.2.1 简介

批次爬虫是一种强大的爬虫模板，支持定时批次爬取任务，使用户能够按照指定的时间间隔自动进行数据爬取和更新。通过选择不同的时间级别（如秒级、分钟级、小时级、天级、周级、月级、季级和年级），用户可以灵活设定爬取间隔，适用于各种需要定期增量或更新数据的场景。

这种爬虫的优势在于它提供了自动化的爬取和更新功能，无需用户手动触发爬取操作，极大地减轻了用户的工作负担，同时提高了数据更新的效率。用户只需在配置中设定好爬虫的时间间隔和定时规则，就能轻松实现数据的定时更新，确保数据始终保持最新和完整。

批次爬虫的灵活性也值得一提。用户可以根据不同的需求设定不同的定时级别，从秒级到年级，确保数据更新频率与业务需求相匹配。例如，对于实时性要求较高的数据，可以选择秒级或分钟级的定时爬取；而对于相对稳定的数据，可以选择天级、周级、月级甚至年级的定时爬取。

总的来说，批次爬虫是一个高效、自动化、灵活的爬虫模板，为用户提供了方便的数据爬取和更新方案。它是处理定期增量或更新数据的理想工具，能够有效提升数据采集的效率和数据的准确性。

#### 5.2.2 特点

- 支持多级定时批次爬取，可以选择秒级、分钟级、小时级、天级、周级、月级、季级、年级定时。
- 可灵活设置爬虫启动时间和爬取间隔，根据具体需求进行定时配置。
- 提供回调函数，用于爬虫单次启动前、结束前、登录等环节的定制操作。

#### 5.2.3 属性和方法

属性：

批次爬虫的属性继承自普通爬虫，包括`name`、`source`、`target`、`description`、`version`等。

此外，批次爬虫还包含以下属性：

- `level`: 爬虫批次级别，用于指定定时的级别，可以是秒级、分钟级、小时级、天级、周级、月级、季级、年级。
- `interval`: 爬虫批次时间间隔，用于指定定时的时间间隔。

方法：

批次爬虫的方法继承自普通爬虫，包括`set_name`、`get_running_time`、`get_remaining_time`、`spider_open`、`spider_close`、`start_requests`、`parse`、`default_parse`等。

批次爬虫还包含以下方法：

- `is_time_to_run(self)`: 判断当前是否是进行爬取的时间。
- `get_next_time(self)`: 获取下一次执行爬取的时间。

#### 5.2.4 使用

使用批次爬虫时，可以按照以下步骤进行：

1. 创建一个继承自 `BatchSpider` 类的新批次爬虫类，根据实际需求在类中添加属性和方法。
2. 在新批次爬虫类中设置定时级别和时间间隔，以及爬虫启动时间。
3. 在新批次爬虫类中实现`create_task`方法，用于创建爬虫任务并保存。
4. 在新批次爬虫类中实现`is_time_to_run`方法，判断当前是否是进行爬取的时间。
5. 在新批次爬虫类中实现`get_next_time`方法，用于获取下一次执行爬取的时间。
6. 在新批次爬虫类中实现`start_requests`方法和`parse`方法，与普通爬虫类相同。
7. 根据需要，在`__init__`方法中传入相应的参数，如登录用户名、密码、cookies等。
8. 启动引擎，导入爬虫实例或爬虫类，爬取数据将按照设定的定时级别和时间间隔进行。

以下是一个使用批次爬虫的示例代码：

```python
from AioSpider.spider import BatchDaySpider
from AioSpider.http import Request


class MyBatchSpider(BatchDaySpider):
    
    name = "批次爬虫示例"
    source = "示例网"
    target = "http://example.com/data"
    description = "这是一个批次爬虫小demo"

    start_urls = ["http://example.com/data"]

    def parse(self, response: Response):
        # 解析响应数据并提取所需信息
        data = response.json
        # 处理数据的逻辑
        ...

        
if __name__ == "__main__":
    
    from AioSpider.core import Engine
        
    engine = Engine()
    engine.add_spider(MyBatchSpider, time='08:00:00')
    engine.start()

```

## 第六章 响应解析

AioSpider 是通过管理 Parse 对象来进行页面解析和提取的，包含正则提取和 xpath 两种解析模式，支持链式调用提取。

### 6.1 属性和方法

| 名称          | 属性或方法 | 释义                                         | 参数                                          | 返回值                     |
| ------------- | ---------- | -------------------------------------------- | --------------------------------------------- | -------------------------- |
| text          | 属性       | 获取文本                                     | 无                                            | str                        |
| json          | 属性       | 提取json                                     | 无                                            | dict                       |
| strip_text    | 方法       | 获取文本，并去除尾部空格、<br>换行符、制表符 | strip：去除尾部符号，默认为None               | str                        |
| extract       | 方法       | 提取列表                                     | 无                                            | Union[str, list, _Element] |
| extract_first | 方法       | 提取列表中第一个元素                         | 无                                            | Union[str, _Element]       |
| extract_last  | 方法       | 提取列表中最后一个元素                       | 无                                            | Union[str, _Element]       |
| re            | 方法       | 正则提取                                     | query: 正则表达式<br>flags: 匹配模式，默认为0 | Parse 对象                 |
| xpath         | 方法       | xpath提取                                    | query: xpath表达式                            | Parse 对象                 |
| empty         | 属性       | 判断 Parse 对象是否为空                      | 无                                            | bool                       |

### 6.2 解析响应（re和xpath的链式调用）

以百度为例，匹配 ”hao123“ 中的数字和”百度一下“，以下图红框中所示

![baidu](D:\AioSpider\assets\baidu.png)

代码如下：

```python
from AioSpider.spider import Spider


class BaiduSpider(Spider):

    start_urls = [
        'https://www.baidu.com/'
    ]

    def parse(self, response):
        # 匹配百度一下
        text1 = response.xpath('//*[@id="su"]/@value').text
        # 匹配数字123
        text2 = response.xpath('//*[@id="s-top-left"]/a[2]/text()').re('\d+').text
        print(text1, text2)


if __name__ == '__main__':
    spider = BaiduSpider()
    spider.start()

```

代码解释：

以下一行代码用于提取响应（Response）中的"百度一下"文本字符串。`response.xpath` 会返回一个 Parse 对象，而 `text` 属性则用于获取 Parse 对象中的匹配结果。

```python
text1 = response.xpath('//*[@id="su"]/@value').text
```

接下来的一行代码用于提取数字123。通过链式调用，我们同时使用了 `xpath` 和正则表达式。

```python
text2 = response.xpath('//*[@id="s-top-left"]/a[2]/text()').re('\d+').text
```

这个示例展示了如何在 AioSpider 框架中利用 `xpath` 和正则表达式进行数据提取。借助这些强大的解析工具，您可以轻松地完成各种数据抓取任务。

## 第七章 中间件

### 7.1 什么是中间件

在 AioSpider 中，中间件是一种特殊的处理模块，负责在请求和响应之间添加额外的处理逻辑。中间件可分为两类：一类是位于网络端的下载器中间件，另一类是位于爬虫端的爬虫中间件。

下载器中间件主要负责在请求发送至目标网站之前对其进行处理，如修改请求头、添加代理等，同时也可以在响应数据返回至爬虫之前对响应数据进行处理，如解码、解压等。这种中间件提供了对网络请求和响应的细粒度控制，使得爬虫更加灵活和可扩展。

爬虫中间件则位于爬虫端，它在爬虫接收到网络响应之前和处理完数据后发出新请求之前，对数据进行进一步处理。这种中间件可以用于实现数据清洗、过滤、异常处理等功能。通过使用爬虫中间件，开发者可以更轻松地为爬虫添加新功能，使爬虫更加强大和易于维护。

综上所述，中间件是 AioSpider 框架的核心组件之一，它们协同工作，为开发者提供了更高层次的抽象，使得爬虫开发变得更加简单、高效。

### 7.2 中间件的作用

中间件在 AioSpider 框架中起着至关重要的作用，它为开发者提供了在请求和响应过程中的可插拔式处理模块。中间件可以灵活地扩展爬虫的功能，提高爬虫的可维护性和稳定性。

中间件的主要作用有以下几点：

1. 对请求和响应进行预处理：通过对请求头、代理设置等进行修改，以及在响应数据返回之前对数据进行解码、解压等操作，中间件为开发者提供了对网络请求和响应的细粒度控制。
2. 数据清洗和过滤：爬虫中间件可以在爬虫接收到网络响应之前，对数据进行清洗和过滤，从而简化后续数据处理流程。
3. 异常处理：中间件可以捕获和处理在请求和响应过程中可能出现的异常，提高爬虫的健壮性。
4. 提高可扩展性：通过使用中间件，开发者可以为爬虫轻松地添加新功能，使得爬虫更加强大和易于维护。
5. 代码解耦：中间件将不同功能模块隔离，使得每个模块职责明确、易于理解，从而提高了代码的可读性和可维护性。

总之，中间件为 AioSpider 框架提供了强大的扩展能力，使得爬虫开发变得更加简单、高效。通过使用中间件，开发者可以轻松地实现各种复杂的爬虫功能，提高爬虫的性能和稳定性。

### 7.3 中间件基类

AioSpider 中有三种中间件基类，同步中间件基类（Middleware）、异步中间件基类（AsyncMiddleware）、异常中间件基类（ErrorMiddleware）。

Middleware 和 AsyncMiddleware 属性

| 属性名   | 指向               |
| -------- | ------------------ |
| spider   | 当前运行的爬虫实例 |
| settings | 当前爬虫加载的配置 |

Middleware 和 AsyncMiddleware 方法

| 方法名           | 参数               | 描述           | 返回值                                                       |
| ---------------- | ------------------ | -------------- | ------------------------------------------------------------ |
| process_request  | request：请求实例  | 处理请求       | Request: 交由引擎重新调度该Request对象 <br>Response: 交由引擎重新调度该Response对象 <br>None: 正常，继续往下执行 穿过下一个中间件 <br>False: 丢弃该Request或Response对象 |
| process_response | response：响应实例 | 处理响应       | Request: 交由引擎重新调度该Request对象<br>Response: 交由引擎重新调度该Response对象 <br/>None: 正常，继续往下执行 穿过下一个中间件 <br/>False: 丢弃该Request或Response对象 |
| spider_open      | spider：爬虫实例   | 爬虫打开时回调 | 无                                                           |
| spider_close     | spider：爬虫实例   | 爬虫关闭时回调 | 无                                                           |

ErrorMiddleware 方法

| 方法名            | 参数                                 | 描述           | 返回值                                                       |
| ----------------- | ------------------------------------ | -------------- | ------------------------------------------------------------ |
| process_exception | request：请求实例<br>exception：异常 | 处理异常       | Request: 交由引擎重新调度该Request对象 <br/>Response: 交由引擎重新调度该Response对象 <br/>None: 正常，继续往下执行 穿过下一个中间件 <br/>False: 丢弃该Request或Response对象 <br/>exception: 将会抛出该异常 |
| spider_open       | spider（爬虫实例）                   | 爬虫打开时回调 | 无                                                           |
| spider_close      | spider（爬虫实例）                   | 爬虫关闭时回调 | 无                                                           |

### 7.4 如何自定义下载中间件

使用中间件时，需继承 AioSpider 中的基类，然后将注册到 settiongs.py 的 DOWNLOAD_MIDDLEWARE 或者 SPIDER_MIDDLEWARE 列表中。

#### 7.4.1 自定义同步中间件

以代理池为例：

```python
import random
from AioSpider.middleware import Middleware


class ProxyPoolMiddleware(Middleware):

    proxy = [
        'http://exzaple1.cn:8888',
        'http://exzaple2.cn:8888',
        'http://exzaple3.cn:8888',
        'http://exzaple4.cn:8888',
        'http://exzaple5.cn:8888',
    ]

    def process_request(self, request):
        # 设置代理
        proxy = random.choice(self.proxy)
        request.proxy = proxy
        return None
    
    def process_response(self, response):
        return None
```

将 ProxyPoolMiddleware 注册到 settings.py 的 DOWNLOAD_MIDDLEWARE 中激活：

```python
DOWNLOAD_MIDDLEWARE = {
    ...
    "ExzapleProject.middleware.ProxyPoolMiddleware": 108,
}
```

#### 7.4.2 自定义异步中间件

一般情况下，只有涉及到异步操作时才用异步中间件，下面只是简单演示异步中间件如何自定义。

以代理池为例：

```python
import random
from AioSpider.middleware import AsyncMiddleware


class ProxyPoolMiddleware2(AsyncMiddleware):

    proxy = [
        'http://exzaple1.cn:8888',
        'http://exzaple2.cn:8888',
        'http://exzaple3.cn:8888',
        'http://exzaple4.cn:8888',
        'http://exzaple5.cn:8888',
    ]

    async def process_request(self, request):
        # 设置代理
        proxy = random.choice(self.proxy)
        request.proxy = proxy
        return None
    
    async def process_response(self, response):
        return None
```

将 ProxyPoolMiddleware2 注册到 settings.py 的 DOWNLOAD_MIDDLEWARE 中激活：

```python
DOWNLOAD_MIDDLEWARE = {
    ...
    "ExzapleProject.middleware.ProxyPoolMiddleware2": 108,
}
```

#### 7.4.3 自定义异常中间件

```python
from AioSpider.middleware import ErrorMiddleware


class TimeoutErrorMiddleware(ErrorMiddleware):

    def process_exception(self, request, exception):
        if isinstance(exception, exceptions.TimeoutError):
            logger.error(f'网络连接超时：{request}')

        return None
```

将 TimeoutErrorMiddleware 注册到 settings.py 的 DOWNLOAD_MIDDLEWARE 中激活：

```python
DOWNLOAD_MIDDLEWARE = {
    ...
    "ExzapleProject.middleware.TimeoutErrorMiddleware": 108,
}
```

### 7.5 如何自定义爬虫中间件

```python
from AioSpider.middleware import SpiderMiddleware


class DemoMiddleware(SpiderMiddleware):

    def process_request(self, request):

	    if '_' in request.params:
            print('params 参数中有时间戳')

         return None

    def process_response(self, response):
        return None
```

将 DemoMiddleware 注册到 settings.py 的 SPIDER_MIDDLEWARE 中激活：

```python
SPIDER_MIDDLEWARE = {
    ...
    "ExzapleProject.middleware.DemoMiddleware": 108,
}
```

### 7.6 内置中间件

#### 7.6.1 下载中间件

| 名称                   | 释义                                                         |
| ---------------------- | ------------------------------------------------------------ |
| FirstMiddleware        | 最先执行的中间件，请求将会最先通过，响应将会最后通过该中间件 |
| HeadersMiddleware      | 请求头处理的中间件，启用该中间件将会自动生成 UA 请求头       |
| RetryMiddleware        | 重试中间件，启用该中间件将会自动重试指定的异常状态码         |
| ProxyMiddleware        | 代理中间件                                                   |
| LastMiddleware         | 最后执行的中间件，请求将会后先通过，响应将会最先通过该中间件 |
| TimeoutErrorMiddleware | 请求超时中间件                                               |
| ExceptionMiddleware    | 异常中间件                                                   |
| BrowserMiddleware      | 浏览器渲染中间件                                             |

BrowserMiddleware 方法和属性

| 名称             | 方法或属性 | 释义        |
| ---------------- | ---------- | ----------- |
| browser          | 属性       | 浏览器集合  |
| driver           | 属性       | 浏览器对象  |
| goto             | 方法       | 页面跳转    |
| refresh          | 方法       | 页面刷新    |
| execut_js        | 方法       | 执行js代码  |
| get_cookies      | 方法       | 获取cookies |
| process_request  | 方法       | 处理请求    |
| process_response | 方法       | 处理响应    |

#### 7.6.2 爬虫中间件

| 名称                                | 释义                                               |
| ----------------------------------- | -------------------------------------------------- |
| AutoConcurrencyStrategyMiddleware   | 自动并发策略                                       |
| RandomConcurrencyStrategyMiddleware | 随机并发策略                                       |
| SpeedConcurrencyStrategyMiddleware  | 速度并发策略，根据设定并发速度系统自动调整         |
| TimeConcurrencyStrategyMiddleware   | 时间并发策略，根据设定并发时间系统自动完成爬取任务 |

`AutoConcurrencyStrategyMiddleware`中间件根据爬虫的平均速度和已运行时间的周期来动态计算任务限制值。根据设定的周期，以及当前运行时间在周期内的比例，使用正弦函数计算任务限制值。任务限制值在最小并发速度和平均速度之间变化，呈现周期性的波动。

`RandomConcurrencyStrategyMiddleware`中间件实现了随机并发策略。它根据爬虫的平均速度和任务限制值之间的关系，动态调整任务限制值。如果任务限制值大于平均速度，将按比例缩小任务限制值，以确保任务不会过载。如果任务限制值小于平均速度，将按比例放大任务限制值，以提高并发性能。

`SpeedConcurrencyStrategyMiddleware`中间件根据设定的平均并发速度自动调整任务限制值。它根据爬虫的平均速度和已运行时间的增长趋势，以及设定的线性关系参数，计算出新的任务限制值。在初始阶段，任务限制值将根据时间的增长而线性增加。超过一定时间后，任务限制值将固定为设定的平均并发速度。

`TimeConcurrencyStrategyMiddleware`中间件根据设定的并发时间来动态调整任务限制值。它根据爬虫的剩余时间和已运行时间的比例，以及设定的总并发时间，计算出新的任务限制值。如果剩余时间较短，任务限制值将适当减小以避免过载。如果剩余时间较长，任务限制值将适当增加以提高并发性能。

这些中间件在爬虫运行过程中根据不同的策略和条件动态调整任务限制值，以实现更有效的并发控制和优化爬虫性能。

## 第八章 ORM

### 8.1 AioSpider ORM

ORM（对象关系映射）是一种编程技术，它将数据库表中的记录映射到 Python 对象中，使得我们可以通过面向对象的方式操作数据库，而无需直接编写 SQL 语句。AioSpider 框架提供了灵活且易用的 ORM 模块，使得开发者能够更加高效地进行数据存储和读取。

#### 8.1.1 ModelConnector

`ModelConnector`是 AioSpider 框架中用于连接数据库的类。它负责初始化和管理数据库连接，并根据配置信息进行相应的初始化。`ModelConnector`支持多种数据库引擎，包括 SQLite、CSV、MySQL、MongoDB 以及普通文件等。通过`ModelConnector`，我们可以在数据模型中灵活地切换和使用不同的数据库。

#### 8.1.2 QuerySet

`QuerySet`是用于执行数据库查询操作的类。它封装了数据库查询的细节，使得我们可以使用类似于 Django ORM 的链式调用方式来进行数据查询。通过`QuerySet`，我们可以轻松地执行过滤、排序、限制等操作，并获取满足条件的数据。

以下是`QuerySet`的一些关键方法：

- `filter(self, **kwargs)`: 添加过滤条件。
- `only(self, *args)`: 选择需要查询的字段。
- `like(self, name, value)`: 添加LIKE条件。
- `limit(self, n: int)`: 限制查询结果数量。
- `exists(self) -> bool`: 判断查询结果是否存在。
- `get(self, **kwargs) -> Optional[Any]`: 获取单条查询结果。
- `all(self, flat=False, **kwargs) -> List[Any]`: 获取多条查询结果。
- `insert(self, items: Union[dict, List[dict]], sql: Optional[str] = None)`: 插入数据。
- `update(self, items: Union[dict, list], where: Union[str, list, tuple] = None)`: 更新数据。
- `delete_one(self, where: dict, sql: str = None, *args, **kwargs) -> None`: 删除单条数据。
- `delete_many(self, where: dict, *args, **kwargs)`: 删除多条数据。

### 8.2 数据模型定义

数据模型是 AioSpider 框架中最重要的部分，它定义了 Python 对象与数据库表之间的映射关系。数据模型继承自`Model`基类，并通过元类`BaseModel`来实现自动化的映射。

以下是一个示例数据模型定义：

```python
class UserAccount(Model):
    username = field.CharField(name='登录账号')
    password = field.CharField(name='登录密码')
    cookies = field.TextField(name='cookies')
    token = field.CharField(name='token')

    order = [
        'id', 'username', 'password', 'cookies', 'token', 'create_time', 'update_time'
    ]
```

在上述示例中，`UserAccount`是一个数据模型类，它继承自`Model`基类。数据模型类的属性定义了字段名和对应的数据类型，例如`username`字段为`CharField`类型，`password`字段为`CharField`类型等。

数据模型类还可以定义`Meta`类，用于指定一些数据模型的元信息，例如数据库引擎、表名、配置信息等。`Meta`类可以包含以下属性：

- `engine`: 指定数据模型所使用的数据库引擎，例如'sqlite'、'mysql'等。
- `db`: 指定数据模型所属的数据库名称。
- `tb_name`: 指定数据模型对应的表名。
- `config`: 指定数据库连接的配置信息。
- `auto_update`: 指定是否自动更新数据模型。
- `union_index`: 指定联合索引。
- `union_unique_index`: 指定联合唯一索引。

### 8.3 数据模型的操作

在 AioSpider 框架中，我们可以使用数据模型类进行数据库的增删改查操作。以下是数据模型的一些常用方法：

- `save(self)`: 将数据保存到数据库。
- `delete(self)`: 删除数据。
- `update(self)`: 更新数据。
- `get(self, **kwargs) -> Optional[Any]`: 根据条件获取单条数据。
- `all(self, flat=False, **kwargs) -> List[Any]`: 根据条件获取多条数据。

示例代码：

```python
# 创建数据模型对象并保存到数据库
user = UserAccount(username='test', password='password', cookies='...', token='...')
user.save()

# 更新数据
user.password = 'new_password'
user.update()

# 根据条件查询数据
user = UserAccount.objects.get(username='test')

# 获取多条数据
users = UserAccount.objects.all(username='test')
```

### 8.4 字段类型

AioSpider 字段模块提供了丰富的字段类型用于定义数据模型，下面将介绍 AioSpider 中的字段类型及其用法。

AioSpider 中的字段类型主要包括以下几种：

- Field
- CharField
- HashField
- PathField
- ExtensionNameField
- BytesContentField
- JSONField
- IPAddressField
- UUIDField

每种字段类型都源于自 Field 类，并可以通过参数进行定制化配置。

#### 8.4.1 普通字段

##### Field 类

Field 类是 AioSpider 字段模块的基类，所有其他字段类型都是基于该类进行扩展。以下是 Field 类的一些主要属性和方法：

属性

- name：字段名
- db_column：数据库列名
- max_length：字段的最大长度
- min_length：字段的最小长度
- primary：是否为主键
- unique：是否为唯一键
- db_index：是否为数据库索引
- null：字段是否可以为空
- default：字段的默认值
- is_save：字段是否参与数据库保存
- validators：字段的验证器列表

方法

- clean：对字段参数进行清理和验证
- `__get__`：获取字段值
- `__set__`：字段值验证
- `__eq__`：判断字段值是否相等
- `__str__`：返回字段的字符串表示
- `__repr__`：返回字段的字符串表示

##### CharField类型

CharField 是 AioSpider 中的字符串类型字段，用于存储文本数据。以下是 CharField 的一些主要属性：

- choices：字段的可选值
- regex：用于验证字段值的正则表达式
- is_truncate：是否截断超出最大长度的字段值
- strip：是否去除字段值两端的空格

##### HashField类型

HashField 是 AioSpider 中的哈希字段类型，用于存储哈希值。以下是 HashField 的一些主要属性：

- make_hash_field：用于生成哈希的字段名或字段列表
- exclude_field：排除在生成哈希时不参与计算的字段名或字段列表

##### PathField类型

PathField 是 AioSpider 中的路径字段类型，用于存储文件路径。以下是 PathField 的一些主要属性：

- regex：用于验证字段值是否为合法路径

##### ExtensionNameField类型

ExtensionNameField 是 AioSpider 中的文件扩展名字段类型，用于存储文件的扩展名。

##### BytesContentField类型

BytesContentField 是 AioSpider 中的字节内容字段类型，用于存储字节数据。以下是 BytesContentField 的一些主要属性：

- encoding：字节内容的编码方式
- regex：用于验证字段值是否符合正则表达式

##### JSONField类型

JSONField 是 AioSpider 中的 JSON 字段类型，用于存储 JSON 格式的数据。

##### IPAddressField类型

IPAddressField 是 AioSpider 中的 IP 地址字段类型，用于存储 IPv4 地址。

##### UUIDField类型

UUIDField 是 AioSpider 中的 UUID 字段类型，用于存储 UUID 值。

#### 8.4.2 时间类型

##### StampField

`StampField` 是继承自 `BigIntField` 的时间戳字段类，用于存储时间戳信息。具有以下属性：

- `auto_add`: 布尔值，表示是否在插入数据时自动添加时间戳，默认为 `False`。
- `auto_update`: 布尔值，表示是否在更新数据时自动更新时间戳，默认为 `False`。

此字段支持的数据类型有 `int`、`datetime`、`date`、`float` 和 `str`，当赋值为时间对象时，直接保存；当为 `str` 类型时，将尝试将字符串转换为时间戳；当赋值为 `None` 时，根据设置的 `auto_add` 和 `auto_update` 来决定是否添加或更新时间戳。

##### DateField

`DateField` 是继承自 `Field` 的日期字段类，用于存储日期信息。没有特殊属性。

此字段支持的数据类型有 `date`、`datetime` 和 `str`，当赋值为日期对象时，直接保存；当为 `str` 类型时，将尝试将字符串转换为日期对象；当赋值为 `None` 时，根据字段的 `default` 和 `null` 属性来确定默认值。

##### TimeField

`TimeField` 是继承自 `Field` 的时间字段类，用于存储时间信息。没有特殊属性。

此字段支持的数据类型有 `time`、`datetime` 和 `str`，当赋值为时间对象时，直接保存；当为 `str` 类型时，将尝试将字符串转换为时间对象；当赋值为 `None` 时，根据字段的 `default` 和 `null` 属性来确定默认值。

##### DateTimeField

`DateTimeField` 是继承自 `DateField` 的日期时间字段类，用于存储日期时间信息。具有以下属性：

- `auto_add`: 布尔值，表示是否在插入数据时自动添加当前日期时间，默认为 `False`。
- `auto_update`: 布尔值，表示是否在更新数据时自动更新当前日期时间，默认为 `False`。

此字段支持的数据类型有 `datetime`、`date`、`int`、`float` 和 `str`，当赋值为日期时间对象时，直接保存；当为 `str` 类型时，将尝试将字符串转换为日期时间对象；当赋值为 `None` 时，根据设置的 `auto_add` 和 `auto_update` 来决定是否添加或更新当前日期时间。

#### 8.4.3 索引类

##### SpatialIndexField

`SpatialIndexField` 是继承自 `IndexMeta` 的空间索引类，用于在数据库中创建空间索引。

##### FullTextIndexField

`FullTextIndexField` 是继承自 `IndexMeta` 的全文索引类，用于在数据库中创建全文索引。

##### UniqueIndexField

`UniqueIndexField` 是继承自 `IndexMeta` 的唯一索引类，用于在数据库中创建唯一索引。

##### NormalIndexField

`NormalIndexField` 是继承自 `IndexMeta` 的普通索引类，用于在数据库中创建普通索引。

##### UnionIndexField

`UnionIndexField` 是继承自 `IndexMeta` 的联合索引类，用于在数据库中创建联合索引。

##### UniqueUnionIndexField

`UniqueUnionIndexField` 是继承自 `IndexMeta` 的唯一联合索引类，用于在数据库中创建唯一联合索引。

#### 8.4.4 文本类型

##### TextField类型

TextField 是 AioSpider 中的文本字段类型，用于存储较长的文本数据。以下是 TextField 的一些主要属性：

- max_length：字段的最大长度（默认为65535）
- min_length：字段的最小长度
- strip：是否去除字段值两端的空格

##### MediumTextField类型

MediumTextField 是 AioSpider 中的中等文本字段类型，用于存储更大的文本数据。以下是 MediumTextField 的一些主要属性：

- max_length：字段的最大长度（默认为16777215）

##### LongTextField类型

LongTextField是AioSpider中的长文本字段类型，用于存储最大的文本数据。以下是LongTextField的一些主要属性：

- max_length：字段的最大长度（默认为4294967295）

##### ListField类型

ListField 是 AioSpider 中的列表字段类型，用于存储列表数据。以下是 ListField 的一些主要属性：

- origin：是否将列表原样保存（默认为False）
- join：用于连接列表元素的字符串

#### 5.4.5 整数类型

##### TinyIntField

TinyIntField 是一个用于存储8位整数的字段类。它对应于数据库的 TINYINT 类型。TinyIntField 用于存储范围在0到255之间的整数。

属性

- name: 字段名称。
- db_column: 数据库列名。
- primary: 是否为主键。
- max_length: 最大长度，默认为4。
- unsigned: 是否为无符号整数。
- default: 默认值。
- null: 是否可为空。
- unique: 是否唯一。
- db_index: 是否为数据库索引。
- choices: 可选的值范围。
- validators: 字段值验证器列表。
- is_save: 是否将字段值保存到数据库。

##### SmallIntField

SmallIntField 是一个用于存储16位整数的字段类。它对应于数据库的 SMALLINT 类型。SmallIntField 用于存储范围在-32,768到32,767之间的整数。

字段属性

- name: 字段名称。
- db_column: 数据库列名。
- primary: 是否为主键。
- max_length: 最大长度，默认为6。
- unsigned: 是否为无符号整数。
- default: 默认值。
- null: 是否可为空。
- unique: 是否唯一。
- db_index: 是否为数据库索引。
- validators: 字段值验证器列表。
- is_save: 是否将字段值保存到数据库。

##### MediumIntField

MediumIntField 是一个用于存储24位整数的字段类。它对应于数据库的 MEDIUMINT 类型。MediumIntField 用于存储范围在-8,388,608到8,388,607之间的整数。

属性

- name: 字段名称。
- db_column: 数据库列名。
- primary: 是否为主键。
- max_length: 最大长度，默认为9。
- unsigned: 是否为无符号整数。
- default: 默认值。
- null: 是否可为空。
- unique: 是否唯一。
- db_index: 是否为数据库索引。
- validators: 字段值验证器列表。
- is_save: 是否将字段值保存到数据库。

##### IntField

IntField 是一个用于存储32位整数的字段类。它对应于数据库的INT类型。IntField 用于存储范围在-2,147,483,648到2,147,483,647之间的整数。

属性

- name: 字段名称。
- db_column: 数据库列名。
- primary: 是否为主键。
- max_length: 最大长度，默认为11。
- unsigned: 是否为无符号整数。
- default: 默认值。
- null: 是否可为空。
- unique: 是否唯一。
- db_index: 是否为数据库索引。
- validators: 字段值验证器列表。
- is_save: 是否将字段值保存到数据库。

##### BigIntField

BigIntField 是一个用于存储64位整数的字段类。它对应于数据库的 BIGINT 类型。BigIntField 用于存储范围在-9,223,372,036,854,775,808到9,223,372,036,854,775,807之间的整数。

属性

- name: 字段名称。
- db_column: 数据库列名。
- primary: 是否为主键。
- max_length: 最大长度，默认为20。
- unsigned: 是否为无符号整数。
- default: 默认值。
- null: 是否可为空。
- unique: 是否唯一。
- db_index: 是否为数据库索引。
- validators: 字段值验证器列表。
- is_save: 是否将字段值保存到数据库。

##### AutoIntField

AutoIntField 是一个用于存储自增整数的字段类。每次设置字段值时，其值会自动增加。AutoIntField 用于存储自增的整数值，可用于生成唯一标识符。

属性

- name: 字段名称。
- db_column: 数据库列名。
- primary: 是否为主键。
- max_length: 最大长度，默认为11。
- sep: 自增步长，默认为1。
- default: 默认值。
- null: 是否可为空。
- unique: 是否唯一。
- db_index: 是否为数据库索引。
- validators: 字段值验证器列表。
- is_save: 是否将字段值保存到数据库。

##### BoolField

BoolField 是一个用于存储布尔值的字段类。它对应于数据库的 TINYINT 类型，取值为0或1。BoolField 用于存储布尔值，即True或False。

属性

- name: 字段名称。
- db_column: 数据库列名。
- db_index: 是否为数据库索引。
- default: 默认值。
- null: 是否可为空。
- unique: 是否唯一。
- validators: 字段值验证器列表。
- is_save: 是否将字段值保存到数据库。

#### 5.4.6 小数类型

##### DecimalField

DecimalField是AioSpider字段模块中的一种浮点数字段类型，用于存储高精度的浮点数数据。DecimalField用于存储高精度的浮点数数据，适用于对数值精度要求较高的场景。

属性

- name：字段名
- db_column：数据库列名
- max_length：字段的最大精度位数
- primary：是否为主键
- unique：是否为唯一键
- db_index：是否为数据库索引
- default：字段的默认值
- null：字段是否可以为空
- is_save：字段是否参与数据库保存
- validators：字段的验证器列表

##### FloatField

FloatField是AioSpider字段模块中的一种浮点数字段类型，用于存储标准的浮点数数据。FloatField用于存储标准的浮点数数据，适用于一般数值精度要求的场景。无特殊属性和方法

##### DoubleField

DoubleField是AioSpider字段模块中的一种浮点数字段类型，用于存储双精度浮点数数据。DoubleField用于存储双精度浮点数数据，适用于对数值精度要求更高的场景。无特殊属性和方法

### 8.5 字段验证器

AioSpider 字段验证器模块提供了一系列验证器，用于对字段进行数据校验。下面将介绍 AioSpider 字段验证器模块中的各种验证器，包括MaxLengthValidator、MinLengthValidator、BitSizeValidator、RangeValidator、RegexValidator、EmailValidator、TypeValidator、StrValidator、BytesValidator、IntValidator、BoolValidator、UniumTpyeValidator、DefaultTypeValidator和IndexValidator。这些验证器可以帮助用户对字段的输入数据进行有效的验证，保证数据的合法性和准确性。

#### 8.5.1 Validator

- 描述：验证器的基类，定义了验证器的共有属性和方法。
- 作用：用于继承，创建其他具体的验证器类。

#### 8.5.2 MaxLengthValidator

- 描述：用于检查字符串字段的最大长度。
- 作用：确保字符串字段的值不超过指定的最大长度。

#### 8.5.3 MinLengthValidator

- 描述：用于检查字符串字段的最小长度。
- 作用：确保字符串字段的值不少于指定的最小长度。

#### 8.5.4 BitSizeValidator

- 描述：用于检查数值字段的位数。
- 作用：确保数值字段的值在指定的位数范围内。

#### 8.5.5 RangeValidator

- 描述：用于检查数值字段的范围。
- 作用：确保数值字段的值在指定的范围内。

#### 8.5.6 RegexValidator

- 描述：用于使用正则表达式验证字段值。
- 作用：确保字段值符合指定的正则表达式规则。

#### 8.5.7 EmailValidator

- 描述：用于验证邮箱地址字段。
- 作用：确保邮箱地址字段的值符合邮箱地址的格式规范。

#### 8.5.8 TypeValidator

- 描述：用于检查字段的数据类型。
- 作用：确保字段值的数据类型与指定的类型相匹配。

#### 8.5.9 StrValidator

- 描述：用于验证字符串类型字段。
- 作用：确保字符串字段的值为字符串类型。
- 继承：TypeValidator。

#### 8.5.10 BytesValidator

- 描述：用于验证字节类型字段。
- 作用：确保字节类型字段的值为字节类型。
- 继承：TypeValidator。

#### 8.5.11 IntValidator

- 描述：用于验证整数类型字段。
- 作用：确保整数类型字段的值为整数类型。
- 继承：TypeValidator。

#### 8.5.12 BoolValidator

- 描述：用于验证布尔类型字段。
- 作用：确保布尔类型字段的值为布尔类型。
- 继承：TypeValidator。

#### 8.5.13 UniumTpyeValidator

- 描述：用于验证字段值是否为指定类型之一。
- 作用：确保字段值的数据类型与指定类型之一相匹配。

#### 8.5.14 DefaultTypeValidator

- 描述：用于验证字段的默认值类型。
- 作用：确保字段的默认值数据类型与指定类型相匹配。
- 继承：UniumTpyeValidator。

#### 8.5.15 IndexValidator

- 描述：用于验证字段是否为索引类型。
- 作用：确保字段是否为索引类型，可以是普通索引或自定义索引类型。

## 第九章 配置文件

### 9.1 系统相关配置

#### 9.1.1 SystemConfig

```python
class SystemConfig:    
    """系统配置项"""
    AioSpiderPath = Path(__file__).parent               # 工作路径
    BackendCacheEngine = BackendEngine.queue            # url缓存方式，默认 queue（队列引擎），redis（redis引擎）
```

#### 9.1.2 LoggingConfig

```python
class LoggingConfig:
    """日志配置"""

    Console = {
        'engine': True,                                 # 是否打印到控制台
        'format': Formater.A,                           # 日志格式
        'time_format': TimeFormater.A,                  # 时间格式
        'level': LogLevel.DEBUG                         # 日志等级
    }
    File = {
        'engine': True,                                 # 是否写文件
        'path': SystemConfig.AioSpiderPath / "log",     # 日志存储路径
        'format': Formater.A,                           # 日志格式
        'time_format': TimeFormater.A,                  # 时间格式
        'level': LogLevel.DEBUG,                        # 日志等级
        'mode': WriteMode.A,                            # 写文件的模式
        'size': 50 * 1024 * 1024,                       # 每个日志文件的默认最大字节数
        'encoding': 'utf-8',                            # 日志文件编码
        'retention': '1 week',                          # 日志保留时间
        'compression': True                             # 是否将日志压缩
    }
```

### 9.2 爬虫相关配置

#### 9.2.1 SpiderRequestConfig

```python
class SpiderRequestConfig:
    """请求配置"""

    REQUEST_USE_SESSION = False                     # 使用会话
    REQUEST_USE_METHOD = RequestMethod.aiohttp      # 使用 aiohttp 库进行请求

    NO_REQUEST_SLEEP_TIME = 3                       # 求情队列无请求时休眠时间
    REQUEST_CONCURRENCY_SLEEP = 1                   # 单位秒，每 task_limit 个请求休眠1秒
    PER_REQUEST_SLEEP = 0                           # 单位秒，每并发1个请求时休眠1秒
    REQUEST_TIMEOUT = 300                           # 请求最大超时时间

    RETRY_ENABLED = True                            # 请求失败是否要重试
    MAX_RETRY_TIMES = 3                             # 每个请求最大重试次数，RETRY_ENABLE指定为True时生效
    RETRY_STATUS = [400, 403, 404, 500, 503]        # 重试状态码，MAX_RETRY_TIMES大于0和RETRY_ENABLE指定为True时生效

    DepthPriority = True                            # 深度优先

    RANDOM_HEADERS = True                           # 随机UserAgent
    # 默认请求头，优先级：spider headers > 默认headers > random headers
    HEADERS = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    # 字符串类型或可迭代对象，值为chrome, ie, opera, firefox, ff, safari，若指定RANDOM_HEADERS为True时则不生效
    USER_AGENT_TYPE = UserAgent.CHROME

```

#### 9.2.2 ConcurrencyStrategyConfig

```python
class ConcurrencyStrategyConfig:
    """
    爬虫并发策略. auto 自动模式，系统不干预；random 随机模式，并发速度随机于最大和最
    小并发速度之间；smart 智能模式，系统自动调节
    """

    exclusive = True						  # 互斥类，下列选项中只能有1个选项为True

    auto = {
        'enabled': False,                       # 是否启用
        'min_concurrency_speed': 20,            # 最小并发数量
    }
    random = {
        'enabled': False,                       # 是否启用
        'min_concurrency_speed': 10,            # 最小并发速度 单位：个/秒
        'max_concurrency_speed': 30,            # 最小并发速度 单位：个/秒
    }
    speed = {
        'enabled': True,                        # 是否启用
        'avg_concurrency_speed': 20,            # 平均并发速度 单位：个
    }
    time = {
        'enabled': False,                       # 是否启用
        'second': 10 * 60,                      # 最小并发速度 单位：个
    }
    fix = {
        'enabled': False,                       # 是否启用
        'task_limit': 10                        # 任务并发数
    }
```

#### 9.2.3 ConnectPoolConfig

```python
class ConnectPoolConfig:
    """连接池"""

    MAX_CONNECT_COUNT = 10                  # 请求最大连接数，指定为 True 时无限制
    USE_DNS_CACHE = True                    # 使用内部DNS映射缓存，用来查询DNS，使建立连接速度更快
    TTL_DNS_CACHE = 10                      # 查询过的DNS条目的失效时间，None表示永不失效
    FORCE_CLOSE = False                     # 连接释放后关闭底层网络套接字
    VERIFY_SSL = True                       # ssl证书验证
    LIMIT_PER_HOST = 0                      # 同一端点并发连接总数，同一端点是具有相同 host、port、ssl 信息，如果是0则不做限制
```

#### 9.2.4 RequestProxyConfig

```python
class RequestProxyConfig:
    """代理配置"""

    # 代理类型，None: 不使用代理、system: 使用系统代理、pool: 使用AioSpider内置代理池、appoint: 手动指定proxy_pool
    proxy_type = ProxyType.none             # 代理类型
    # 代理池配置
    proxy_pool = {
        'name': 'proxy_pool',               # redis 数据库对应的键名
        'PROXY_FETCHER': [
            "free_proxy01", "free_proxy02", "free_proxy03", "free_proxy04", "free_proxy05",
            "free_proxy06", "free_proxy07", "free_proxy08", "free_proxy09", "free_proxy10"
        ],                                  # 代理源
        'HTTP_URL': "http://httpbin.org",   # 代理验证目标网站
        'HTTPS_URL': "https://www.qq.com",
        'VERIFY_TIMEOUT': 10,               # 代理验证时超时时间
        'MAX_FAIL_COUNT': 0,                # 近PROXY_CHECK_COUNT次校验中允许的最大失败次数,超过则剔除代理
        'MAX_FAIL_RATE': 0.1,               # 近PROXY_CHECK_COUNT次校验中允许的最大失败率,超过则剔除代理
        'POOL_SIZE_MIN': 20,                # proxyCheck时代理数量少于POOL_SIZE_MIN触发抓取
        'PROXY_REGION': True,               # 是否启用代理地域属性
        'TIMEZONE': "Asia/Shanghai"
    }
    address = None                          # 代理地址，ip:port，当 type 指定为 appoint 时，需要设置。None、str、list
```

#### 9.2.5 DOWNLOAD_MIDDLEWARE

```python
# 下载中间件
DOWNLOAD_MIDDLEWARE = {
    "AioSpider.middleware.download.FirstMiddleware": 100,           # 优先中间件
    "AioSpider.middleware.download.HeadersMiddleware": 101,         # 请求头中间件
    "AioSpider.middleware.download.LastMiddleware": 102,            # 最后中间件
    "AioSpider.middleware.download.RetryMiddleware": 103,           # 请求重试中间件
    "AioSpider.middleware.download.ProxyMiddleware": 104,           # 代理池中间件
    "AioSpider.middleware.download.ExceptionMiddleware": 105,       # 异常中间件
}
```

#### 9.2.6 SPIDER_MIDDLEWARE

```python
# 爬虫中间件
SPIDER_MIDDLEWARE = {
    "AioSpider.middleware.spider.AutoConcurrencyStrategyMiddleware": 100,       # 自动并发爬虫中间件
    "AioSpider.middleware.spider.RandomConcurrencyStrategyMiddleware": 101,     # 随机并发爬虫中间件
    "AioSpider.middleware.spider.SpeedConcurrencyStrategyMiddleware": 102,      # 速度并发爬虫中间件
    "AioSpider.middleware.spider.TimeConcurrencyStrategyMiddleware": 103,       # 时间并发爬虫中间件
}
```

#### 9.2.7 DataFilterConfig

```python
class DataFilterConfig:
    """数据去重"""

    COMMIT_SIZE = 1000                      # 数据每批提交保存的数量
    MODEL_NAME_TYPE = 'smart'               # lower / upper / smart，处理表明的方式

    DATA_FILTER_ENABLED = False             # 是否启用数据去重
    CACHED_ORIGIN_DATA = False              # 是否启用缓存原始数据 数据量大的时候建议设置为True，每次启动将会自动去重
    BLOOM_CAPACITY = 5000 * 10000           # 布隆过滤器数据容量
```

#### 9.2.8 RequestFilterConfig

```python
class RequestFilterConfig:
    """URL去重"""

    Enabled = True,                                     # 是否缓存爬过的请求 将爬过的请求缓存到本地
    LoadSuccess = True                                  # 将CACHED_REQUEST缓存中成功的请求加载到队列
    LoadFailure = False                                 # 将CACHED_REQUEST缓存中失败的请求加载到队列
    ExpireTime = 60 * 60 * 24                           # 缓存时间 秒
    CachePath = SystemConfig.AioSpiderPath / "cache"    # 数据和资源缓存路径
    FilterForever = True                                # 是否永久去重，配置此项 CACHED_EXPIRE_TIME 无效

    IgnoreStamp = True                                  # 去重忽略时间戳
    ExcludeStampNames = ['_']                           # 时间戳字段名，一般指请求中params、data中的参数
```

#### 9.2.9 BrowserConfig

```python
class BrowserConfig:
    """浏览器配置"""

    exclusive = True

    class Chromium:

        enabled = False                                                 # 是否开启浏览器
        LogLevel = 3                                                    # 日志等级
        Proxy = None                                                    # 代理
        HeadLess = False                                                # 是否无头模式
        Options = None                                                  # 启动参数
        UserAgent = None                                                # user_agent
        ProfilePath = None                                              # 用户数据路径
        ExtensionPath = None                                            # 拓展应用路径
        DisableImages = False                                           # 禁用图片
        DisableJavaScript = False                                       # 禁用js
        ExecutePath = Browser.CHROMIUM_DRIVER_PATH                      # chrome webdriver 路径
        BinaryPath = Browser.CHROMIUM_BINARY_PATH                       # 浏览器路径
        DownloadPath = SystemConfig.AioSpiderPath / "download"          # 下载路径

    class Firefox:

        enabled = False                                                 # 是否开启浏览器
        LogLevel = 3                                                    # 日志等级
        Proxy = None                                                    # 代理
        HeadLess = False                                                # 是否无头模式
        Options = None                                                  # 启动参数
        UserAgent = None                                                # user_agent
        ProfilePath = None                                              # 用户数据路径
        ExtensionPath = None                                            # 拓展应用路径
        DisableImages = False                                           # 禁用图片
        DisableJavaScript = False                                       # 禁用js
        ExecutePath = Browser.FIREFOX_DRIVER_PATH                       # chrome webdriver 路径
        BinaryPath = Browser.FIREFOX_BINARY_PATH                        # 浏览器路径
        DownloadPath = SystemConfig.AioSpiderPath / "download"          # 下载路径
```

### 9.3 数据库相关配置

```python
class DataBaseConfig:
    """数据库配置"""

    Csv = {
        'enabled': False,
        'CONNECT': {
            'DEFAULT': {
                'CSV_PATH': SystemConfig.AioSpiderPath / 'data',		# 数据目录
                'ENCODING': 'utf-8',								    # 文件写入编码
                'WRITE_MODE': WriteMode.W							    # 文件写入模式，w/r/a/wb/rb/ab
            },
        }
    }

    Sqlite = {
        'enabled': False,
        'CONNECT': {
            'DEFAULT': {
                'SQLITE_PATH': SystemConfig.AioSpiderPath / 'data',	    # 数据库目录
                'SQLITE_DB': "aioSpider",							    # 数据库名称
                'CHUNK_SIZE': 20 * 1024 * 1024,						    # 每批允许写入最大字节数
                'SQLITE_TIMEOUT': 10								    # 连接超时时间
            },
        }
    }

    Mysql = {
        'enabled': False,
        'CONNECT': {
            'DEFAULT': {
                'MYSQL_HOST': "127.0.0.1",				                # 域名
                'MYSQL_PORT': 3306,						                # 端口
                'MYSQL_DB': "",							                # 数据库名
                'MYSQL_USER_NAME': "",					                # 用户名
                'MYSQL_USER_PWD': "",					                # 密码
                'MYSQL_CHARSET': "utf8mb4",				                # 数据库字符集
                'MYSQL_CONNECT_TIMEOUT': 10,			                # 连接超时时间
                'MYSQL_TIME_ZONE': '+8:00'				                # 时区
            }
        }
    }

    Mongodb = {
        'enabled': False,
        'CONNECT': {
            'DEFAULT': {
                'MONGO_HOST': "127.0.0.1",			                    # 域名
                'MONGO_PORT': 27017,				                    # 端口
                'MONGO_DB': "",						                    # 数据库名
                'MONGO_USER_NAME': "",				                    # 用户名
                'MONGO_USER_PWD': ""				                    # 密码
            }
        }
    }

    File = {
        'enabled': False,
        'CONNECT': {
            'DEFAULT': {
                'FILE_PATH': SystemConfig.AioSpiderPath / 'data',       # 数据目录
                'ENCODING': 'utf-8',							        # 文件写入编码
                'WRITE_MODE': WriteMode.WB							    # 文件写入模式
            },
        }
    }

    Redis = {
        'enabled': False,
        'CONNECT': {
            'DEFAULT': {
                'host': '127.0.0.1',  			                        # 域名
                'port': 6379,					                        # 端口
                'username': None,				                        # 用户名
                'password': None,				                        # 密码
                'db': 0,						                        # 数据库索引
                'encoding': 'utf-8', 			                        # 编码
                'max_connections': 1 * 10000   	                        # 最大连接数
            }
        }
    }

```

### 9.4 消息通知配置

```python
class MessageNotifyConfig:
    """消息通知配置"""

    exclusive = True

    # 钉钉机器人
    DingDingRobot = {
        'enabled': False,
        'ROBOT_TOKEN': [],                      # 钉钉机器人token
        'WARNING_WHO': [],                      # 报警人 将会在群内@此人, 支持列表，可指定多人
        'WARNING_ALL': False,                   # 是否提示所有人， 默认为False
        'WARNING_INTERVAL': 60,                 # 相同报警的报警时间间隔，防止刷屏
        'WARNING_LEVEL': "WARNING",             # 报警级别， DEBUG / ERROR
    },
    # 邮件机器人
    EmailRobot = {
        'enabled': False,
        'EMAIL_SENDER': "",                     # 发件人
        'EMAIL_PASSWORD': "",                   # 授权码
        'EMAIL_RECEIVER': "",                   # 收件人 支持列表，可指定多个
        'EMAIL_SMTPSERVER': "smtp.qq.com",      # 邮件服务器 默认为qq邮箱
        'WARNING_INTERVAL': 60,                 # 相同报警的报警时间间隔，防止刷屏; 0表示不去重
        'WARNING_LEVEL': "WARNING",             # 报警级别， DEBUG / ERROR
    },
    # 微信机器人
    WechatRobot = {
        'enabled': False,
        'ROBOT_API': "",                        # 企业微信机器人api
        'ROBOT_TOKENS': [],                     # 企业微信机器人token
        'WARNING_WHO': [],                      # 报警人 将会在群内@此人, 支持列表，可指定多人
        'WARNING_ALL': False,                   # 是否提示所有人， 默认为False
        'WARNING_INTERVAL': 60,                 # 相同报警的报警时间间隔，防止刷屏; 0表示不去重
        'WARNING_LEVEL': "WARNING",             # 报警级别， DEBUG / ERROR
    }
```



## 第十章 爬虫工具集

### 10.1 文件目录处理

#### 10.1.1 mkdir

创建目录，能创建深层次目录

##### 定义

```python
def mkdir(path: Union[Path, str], auto: bool = True):
	...
```

##### 参数

| 参数 | 释义                                                         | 类型             | 是否必选 | 默认值 |
| ---- | ------------------------------------------------------------ | ---------------- | -------- | ------ |
| path | 文件夹路径                                                   | Union[Path, str] | 是       | 无     |
| auto | 自动判断 path 参数是文件还是文件夹子 。当 auto 为 True 时，会自动判断 path 路径参数是否有文件     后缀（如：.txt、.csv等），如果有则创建父级文件夹，如果没有则创建当前路径文件夹；当 auto 为 False 时，     会已当前路径作为文件夹创建 | bool             | 否       | True   |

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| 无 | None |

##### 使用示例

```python
from AioSpider import tools

# 在D盘的a目录下创建b文件夹，若a文件夹不存在也会自动创建
tools.mkdir(r'D:\a\b')

# tools.mkdir(Path('D:\a\b.txt'))				# 在D盘下创建了a文件夹
# tools.mkdir(Path('D:\a\b.txt'), auto=False)	 # 在D盘的a目录下创建b.txt文件夹
```

### 10.2 时间处理

#### 10.2.1 strtime_to_stamp

时间字符串转时间戳

##### 定义

```python
def strtime_to_stamp(str_time: str, format: str = None, millisecond: bool = False) -> Optional[int]:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 | 默认值 |
| ----- | ------------ | -------- | -------- | -------- |
| str_time  | 时间字符串 |  str  | 是     | 无 |
| format | 时间字符串格式 | str | 否 | None |
| millisecond  | 是否返回毫秒级时间戳 |    bool   | 否  |    False    |

##### 返回值

| 释义   | 类型 |
| ------ | ---- |
| 时间戳 | int  |

##### 使用示例

```python
from AioSpider import tools

# 将'2022/02/15 10:12:40'时间字符串转成时间戳
tools.strtime_to_stamp('2022/02/15 10:12:40')     				  # 1644891160
tools.strtime_to_stamp('2022/02/15 10:12:40', millisecond=True)    # 1644891160000
```

#### 10.2.2 stamp_to_strtime

stamp_to_strtime: 时间戳转时间字符串

##### 定义

```python
def stamp_to_strtime(time_stamp: , format=) -> Optional[str]:
    ...
```

##### 参数

| 参数       | 释义           | 类型                   | 是否必选 | 默认值              |
| ---------- | -------------- | ---------------------- | -------- | ------------------- |
| time_stamp | 时间戳         | Union[int, float, str] | 是       | 无                  |
| format     | 时间字符串格式 | bool                   | 否       | '%Y-%m-%d %H:%M:%S' |

##### 返回值

| 释义       | 类型      |
| ---------- | --------- |
| 时间字符串 | str, None |

##### 使用示例

```python
from AioSpider import tools

# 将 1644891160 时间戳转成时间字符串
tools.stamp_to_strtime(1644891160)    # '2022/02/15 10:12:40'
```

#### 10.2.3 strtime_to_time

时间字符串转日期时间类型

##### 定义

```python
def strtime_to_time(str_time: str, is_date: bool = False) -> Union[datetime, date]:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 | 默认值 |
| ----- | -------- | -------- | -------- | -------- |
| str_time  | 时间字符串 | str  | 是     | 无    |
| format | 时间格式化字符串 | str | 否 | None |
| is_date | 是否返回日期类型 | bool | 否 | False |

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| 日期时间对象 | Union[datetime, date] |

##### 使用示例

```python
from AioSpider import tools

# 将 '2022/02/15 10:12:40' 时间戳转成时间对象
tools.strtime_to_time('2022/02/15 10:12:40') 	                 # datetime.datetime(2022, 2, 15, 10, 12, 40)
tools.strtime_to_time('2022/02/15 10:12:40', format='%Y-%m-%d')  # datetime.datetime(2022, 2, 15, 0, 0, 0)
tools.strtime_to_time('2022/02/15 10:12:40', is_date=True)       # datetime.date(2022, 2, 15)
```

#### 10.2.4 stamp_to_time

时间戳转时间字符串，支持秒级和毫秒级时间戳自动判断

##### 定义

```python
def stamp_to_time(time_stamp: Union[int, float, str], is_date: bool = False, zone: str = '+8:00') -> Union[datetime, date]:
    ...
```

##### 参数

| 参数       | 释义             | 类型                   | 是否必选 | 默认值  |
| ---------- | ---------------- | ---------------------- | -------- | ------- |
| time_stamp | 时间戳           | Union[int, float, str] | 是       | 无      |
| is_date    | 是否返回日期类型 | bool                   | 否       | False   |
| zone       | 时区             | str                    | 否       | '+8:00' |

##### 返回值

| 释义         | 类型                  |
| ------------ | --------------------- |
| 日期时间对象 | Union[datetime, date] |

##### 使用示例

```python
from AioSpider import tools

# 将 1644891160 时间戳转成时间对象
tools.stamp_to_time(1644891160) 				# datetime.datetime(2022, 2, 15, 10, 12, 40)
tools.stamp_to_time(1644891160, is_date=True) 	 # datetime.date(2022, 2, 15)
```

#### 10.2.5 time_to_stamp

时间戳转时间字符串，支持秒级和毫秒级时间戳自动判断

##### 定义

```python
def time_to_stamp(time: Union[datetime, date], millisecond: bool = False) -> int:
    ...
```

##### 参数

| 参数        | 释义                 | 类型                  | 是否必选 | 默认值 |
| ----------- | -------------------- | --------------------- | -------- | ------ |
| time        | 时间序列             | Union[datetime, date] | 是       | 无     |
| millisecond | 是否返回毫秒级时间戳 | bool                  | 否       | False  |

##### 返回值

| 释义   | 类型 |
| ------ | ---- |
| 时间戳 | int  |

##### 使用示例

```python
from datetime import datetime, date
from AioSpider import tools

# 将 1644891160 时间戳转成时间对象
tools.time_to_stamp(date(2022, 1, 1)) 						# 1640966400
tools.time_to_stamp(date(2022, 1, 1), millisecond=True) 	  # 1640966400000
```

#### 10.2.6 before_day

获取时间间隔

##### 定义

```python
def before_day(now: Optional[datetime] = None, before: int = 0, is_date: bool = False) -> Union[datetime, date]:
    ...
```

##### 参数

| 参数    | 释义                                             | 类型     | 是否必选 | 默认值 |
| ------- | ------------------------------------------------ | -------- | -------- | ------ |
| now     | 时间，默认为 None，表示当前时间                  | datetime | 否       | None   |
| before  | 时间，默认为 None，表示今天，-1 为昨天，1 为明天 | int      | 否       | 0      |
| is_date | 是否返回日期对象                                 | bool     | 否       | False  |

##### 返回值

| 释义 | 类型 |
| ---- | ---- |
| 无   | None |

##### 使用示例

```python
from AioSpider import tools

print(datetime.now())						# datetime.datetime(2023, 2, 3, 18, 2, 0, 769453)
tools.before_day(before=1)    		 		 # datetime.datetime(2023, 2, 2, 18, 2, 26, 57416)
tools.before_day(before=1, is_date=True)      # datetime.date(2023, 2, 2)
```

#### 10.2.7 make_timestamp

获取时间戳

##### 定义

```python
def make_timestamp(millisecond: bool = True, to_string: bool = False) -> Union[int, str]:
    ...
```

##### 参数

| 参数        | 释义                   | 类型 | 是否必选 | 默认值 |
| ----------- | ---------------------- | ---- | -------- | ------ |
| millisecond | 是否获取毫秒时间戳     | bool | 否       | True   |
| to_string   | 结果是否返回字符串类型 | bool | 否       | False  |

##### 返回值

| 释义                             | 类型            |
| -------------------------------- | --------------- |
| 时间戳，返回类型和输入参数有关系 | Union[int, str] |

##### 使用示例

```python
from AioSpider import tools

tools.make_timestamp()    		 		 # 1675653040661
tools.make_timestamp(to_string=True)   	  # '1675653062963'
tools.make_timestamp(millisecond=False)   # 1675653090
```

### 10.3 字符串处理

#### 10.3.1 str2num

str2num: 数值类型转化，带有 ,、%、万、百万等格式化数字都能转换，一般用于字符串数字转整型或浮点型

##### 定义

```python
def str2num(string: str, multi: int = 1, force: bool = False, _type: Callable = int) -> Union[int, float, str]:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 | 默认值 |
| ----- | ------------ | -------- | -------- | ------ |
| string  | 字符串       | str      | 是       | 无 |
| multi | 倍乘基数     | int      | 否       | 1      |
| force | 是否强制转换 | bool     | 否       | False  |
| _type | 转换类型 | Callable | 否       | int    |

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| 转换后的数字类型，返回整型或浮点型数字 | Union[int, float, str]|

##### 使用示例

```python
from AioSpider import tools

tools.str2num(string='100')   # 100
tools.str2num(string='100', multi=10)   # 1000
# force 指定为True的情况下才会强转
tools.str2num(string='100', multi=10, _type=float, force=False)# 1000.0
tools.str2num(string='100', multi=10, _type=float, force=True) # 1000.0
tools.str2num(string='100.0', multi=10, _type=float)           # 1000.0
```

#### 10.3.2 aio_eval

执行字符串

##### 定义

```python
def aio_eval(string: str, default: Any = None) -> Any:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 | 默认值 |
| ----- | ------------ | -------- | -------- | ------ |
| string  | 字符串       | str      | 是       | 无 |
| default | 默认值     | Any      | 否       | None |

##### 返回值

| 释义           | 类型 |
| -------------- | ---- |
| 字符串执行结果 | Any  |

##### 使用示例

```python
from AioSpider import tools

tools.aio_eval('print("hello world")')    # hello world
tools.aio_eval('{"a": 1111}')             # {"a": 1111}
tools.aio_eval('1/0', default=100)        # 100 
```

#### 10.3.3 make_md5

计算 md5 值

##### 定义

```python
def get_hash(item: Any) -> str:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 | 默认值 |
| ----- | ------------ | -------- | -------- | -------- |
| item  | md5 待计算值   | Any      | 是       | 无      |

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| 哈希值 | str |

##### 使用示例

```python
from AioSpider import tools
tools.get_hash('hello world')    # '5eb63bbbe01eeed093cb22bb8f5acdc3'
```

#### 10.3.4 make_sha1

计算 sha1 值

##### 定义

```python
def make_sha1(item: Any) -> str:
    ...
```

##### 参数

| 参数 | 释义          | 类型 | 是否必选 | 默认值 |
| ---- | ------------- | ---- | -------- | ------ |
| item | sha1 待计算值 | Any  | 是       | 无     |

##### 返回值

| 释义    | 类型 |
| ------- | ---- |
| sha1 值 | str  |

##### 使用示例

```python
from AioSpider import tools
tools.make_sha1('hello world')    # '2aae6c35c94fcfb415dbe95f408b9ce91ee846ed'
```

#### 10.3.5 make_sha256

计算 sha256 值

##### 定义

```python
def make_sha256(item: Any) -> str:
    ...
```

##### 参数

| 参数 | 释义         | 类型 | 是否必选 | 默认值 |
| ---- | ------------ | ---- | -------- | ------ |
| item | 计算sha256值 | Any  | 是       | 无     |

##### 返回值

| 释义     | 类型 |
| -------- | ---- |
| sha256值 | str  |

##### 使用示例

```python
from AioSpider import tools
tools.make_sha256('hello world')    # 'b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9'
```

#### 10.3.6 filter_type

将 js 中的 null、false、true 过滤并转换成 python 对应的数据类型，常用于 json.loads 前

##### 定义

```python
def filter_type(string: str) -> str:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 | 默认值 |
| ----- | ------------ | -------- | -------- | -------- |
| string  | 代转字符串 |  str     | 是     | 无    |

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| 过滤后新的字符串 | str |

##### 使用示例

```python
from AioSpider import tools
tools.filter_type('{"a": "null", "b": "false"}')    # '{"a": "None", "b": "False"}'
```

#### 10.3.7 join

拼接字符串，若 data 参数中的元素有非字符串类型的元素，会被强转


##### 定义

```python
def join(data: Iterable, on: str = '') -> str:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 | 默认值 |
| ----- | ------------ | -------- | -------- | ------ |
| data  | 待转可迭代对象 |  Iterable  | 是     | 无 |
| on  | 拼接字符 |  str  | 否    | '' |

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| 拼接后新的字符串 | str |

##### 使用示例

```python
from AioSpider import tools

tools.join(['a', 'b', 'c', 'd'])             # 'abcd'
tools.join(['a', 'b', 'c', 'd'], on=',')     # 'a,b,c,d'
```

### 10.4 数值处理

#### 10.4.1 max

求最大值

##### 定义

```python
def max(arry: Iterable, default: Union[int, float] = 0) -> Uniun[int, float]:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 | 默认值 |
| ----- | ------------ | -------- | -------- | -------- |
| arry  | 数组 |  Iterable  | 是     | 无 |
| default  | 默认值 |  Union[int, float]  | 否     |   0     |

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| 数组中的最大值 | Uniun[int, float] |

##### 使用示例

```python
from AioSpider import tools

tools.max([1, 5, 3, 10, 2])    # 10
```

#### 10.4.2 min

求最小值


##### 定义

```python
def min(arry: Iterable, default: Union[int, float] = 0) -> Uniun[int, float]:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 | 默认值 |
| ----- | ------------ | -------- | -------- | -------- |
| arry  | 数组 |  Iterable  | 是     | 无 |
| default  | 默认值 |  Union[int, float]  | 否     |   0     |

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| 数组中的最小值 | Uniun[int, float] |

##### 使用示例

```python
from AioSpider import tools

tools.min([1, 5, 3, 10, 2])    # 1
```

```
round_up
```

#### 10.4.5 round_up

向上取整


##### 定义

```python
def round_up(item: Union[float, int, str]) -> Union[int, float]:
    ...
```

##### 参数

| 参数 | 释义       | 类型                   | 是否必选 | 默认值 |
| ---- | ---------- | ---------------------- | -------- | ------ |
| item | 待取整数据 | Union[float, int, str] | 是       | 无     |

##### 返回值

| 释义             | 类型              |
| ---------------- | ----------------- |
| 取整数据后的数据 | Uniun[int, float] |

##### 使用示例

```python
from AioSpider import tools

tools.round_up(3.3)          # 4
tools.round_up(3)			# 3
tools.round_up('3.3')        # 4
```

### 10.5 网页清洗

#### 10.5.1 clean_html

清洗 html 文本

##### 定义

```python
def clean_html(html: str, remove_tags: Iterable = None, safe_attrs: Iterable = None) -> str:
    ...
```

##### 参数

| 参数        | 释义                                            | 类型     | 是否必选 | 默认值 |
| ----------- | ----------------------------------------------- | -------- | -------- | ------ |
| html        | html 文本                                       | str      | 是       | 无     |
| remove_tags | 移除 html 中不需要的标签，如：['a', 'p', 'img'] | Iterable | 否       | None   |
| safe_attrs  | 保留相关属性，如：['src', 'href']               | Iterable | 否       | None   |

##### 返回值

| 释义             | 类型 |
| ---------------- | ---- |
| 清晰后的html文本 | str  |

##### 使用示例

```python
from AioSpider import tools

html = '''
<div>
	aaaaaaaaaa</br>
	<p>dddddd</p>
	<a href="aaaaaaaa"></a>
</div>
'''
tools.clean_html(html=html, remove_tags=['a', 'p'])   # '<div>aaaaaaaaaadddddd</div>'
```

#### 10.5.2 xpath

xpath 提取数据

##### 定义

```python
def xpath(node: Union[str, etree._Element], query: str, default: Any = None) -> Union[list, etree._Element, str]:
    ...
```

##### 参数

| 参数    | 释义                   | 类型                       | 是否必选 | 默认值 |
| ------- | ---------------------- | -------------------------- | -------- | ------ |
| node    | 元素节点或 html 字符串 | Union[str, etree._Element] | 是       | 无     |
| query   | xpath 表达式           | str                        | 是       | 无     |
| default | 默认值                 | Any                        | 否       | None   |

##### 返回值

| 释义               | 类型                             |
| ------------------ | -------------------------------- |
| xpath 元素节点列表 | Union[list, etree._Element, str] |

##### 使用示例

```python
from AioSpider import tools

html = '<p><span>hellor world</span></p>'
tools.xpath(node=html, query='//span/text()')     # ['hellor world']
# html 若是一个xpath元素节点
tools.xpath(node=html, query='//span/text()')     # ['hellor wo
tools.xpath(node=html, query='//span')            # 返回节点列表
```

#### 10.5.3 xpath_text

xpath 提取文本数据

##### 定义

```python
def xpath_text(node: Union[str, etree._Element], query: str, on: str = None, default: str = None) -> str:
    ...
```

##### 参数

| 参数    | 释义                   | 类型                       | 是否必选 | 默认值 |
| ------- | ---------------------- | -------------------------- | -------- | ------ |
| node    | 元素节点或 html 字符串 | Union[str, etree._Element] | 是       | 无     |
| query   | xpath 表达式           | str                        | 是       | 0      |
| on      | 拼接字符串             | str                        | 否       | ''     |
| default | 默认值                 | str                        | 否       | ''     |

##### 返回值

| 释义               | 类型 |
| ------------------ | ---- |
| xpath 提取的字符串 | str  |

##### 使用示例

```python
from AioSpider import tools

html = '<p><span>hellor world</span></p>'
tools.xpath_text(node=html, query='//span/text()')     # 'hellor world'
# html 若是一个xpath元素节点
tools.xpath(node=html, query='//span/text()')     # 'hellor world"
```

#### 10.5.4 re

正则提取数据

##### 定义

```python
def re(text: str, regx: str, default: Any = None) -> list:
    ...
```

##### 参数

| 参数    | 释义           | 类型 | 是否必选 | 默认值 |
| ------- | -------------- | ---- | -------- | ------ |
| text    | 原始文本字符串 | str  | 是       | 无     |
| regx    | 正则表达式     | str  | 是       | 0      |
| default | 默认值         | Any  | 否       | None   |

##### 返回值

| 释义                       | 类型 |
| -------------------------- | ---- |
| 正则表达式匹配到的元素列表 | list |


##### 使用示例

```python
from AioSpider import tools

text = '<a href="https://www.baidu.com"></a>'
tools.re(text=text, regx='href="(.*?)"')    # ['https://www.baidu.com']
```

#### 10.5.5 re_text

正则提取文本数据

##### 定义

```python
def re_text(text: str, regx: str, on: str = None, default: str = None) -> str:
    ...
```

##### 参数

| 参数    | 释义           | 类型 | 是否必选 | 默认值 |
| ------- | -------------- | ---- | -------- | ------ |
| text    | 原始文本字符串 | str  | 是       | 无     |
| regx    | 正则表达式     | str  | 是       | 0      |
| default | 默认值         | str  | 否       | ''     |

##### 返回值

| 释义                         | 类型 |
| ---------------------------- | ---- |
| 正则表达式匹配到的第一个元素 | str  |

##### 使用示例

```python
from AioSpider import tools

text = '<a href="https://www.baidu.com"></a>'
tools.re_text(text=text, regx='href="(.*?)"') # 'https://www.baidu.com'
```

### 10.6 加解密工具集

#### 10.6.1 aes_encrypt

AES 加密

##### 定义

```python
def aes_encrypt(
        *, enc_str: Union[str, bytes, dict], key: str, mode: int = AES.MODE_ECB, iv: str = None,
        padding: int = PaddingMode.PKCS7Padding, encoding: str = "utf-8"
) -> AESCryptor.MetaData:
    ...
```

##### 参数

| 参数     | 释义                                                         | 类型                    | 是否必选 | 默认值                   |
| -------- | ------------------------------------------------------------ | ----------------------- | -------- | ------------------------ |
| enc_str  | 待加密字符串                                                 | Union[str, bytes, dict] | 是       | 无                       |
| key      | 秘钥                                                         | str                     | 是       | 无                       |
| mode     | 加密模式，可选值有两个：ECB、CBC                             | int                     | 否       | AES.MODE_ECB             |
| iv       | 偏移量                                                       | str                     | 否       | None                     |
| padding  | 填充方式，可选值有三个：NoPadding、ZeroPadding、PKCS7Padding | int                     | 否       | PaddingMode.PKCS7Padding |
| encoding | 编码格式                                                     | str                     | 否       | utf-8                    |

##### 返回值

| 释义                   | 类型 |
| ---------------------- | ---- |
| AES 加密后的base64密文 | str  |

##### 使用示例

```python
from AioSpider import tools

tools.aes_encrypt(enc_str='hello world', key='abcdefghijklmnop')     # 'f7sSBDV0N6MOpRJLpSJL0w=='
```

#### 10.6.2 make_uuid

生成 UUID 字符串

##### 定义

```python
def make_uuid(string: str = None, mode: int = 1, namespace: uuid.UUID = uuid.NAMESPACE_DNS):
    ...
```

##### 参数

| 参数      | 释义                                                         | 类型      | 是否必选 | 默认值             |
| --------- | ------------------------------------------------------------ | --------- | -------- | ------------------ |
| string    | 字符串                                                       | str       | 否       | None               |
| mode      | 模式。可选值有：1: 根据当前的时间戳和 MAC 地址生成；2: 根据 MD5 生成；3: 根据随机数生成；4. 根据 SHA1 生成 | str       | 否       | 1                  |
| namespace | 命名空间，有四个可选值：NAMESPACE_DNS、NAMESPACE_URL、NAMESPACE_OID、NAMESPACE_X500 | uuid.UUID | 否       | uuid.NAMESPACE_DNS |

##### 返回值

| 释义        | 类型 |
| ----------- | ---- |
| uuid 字符串 | str  |

##### 使用示例

```python
from AioSpider import tools

tools.make_uuid()     							  # 'fd895590a6c611ed99435811229c710d'
tools.make_uuid(string='hello world', mode=2)		# '11f3c98eee6f32d693cc8ea97b77b2a0'
```

### 10.7 网络协议

#### 10.7.1 extract_params

从 url 中提取参数

##### 定义

```python
def extract_params(url: str) -> dict:
    ...
```

##### 参数

| 参数 | 释义 | 类型 | 是否必选 | 默认值 |
| ---- | ---- | ---- | -------- | ------ |
| url  | url  | str  | 是       | 无     |

##### 返回值

| 释义                       | 类型 |
| -------------------------- | ---- |
| 从 url 中提取的 query 参数 | dict |

##### 使用示例

```python
from AioSpider import tools
	
url = 'http://127.0.0.1:5025/ip?a=1&b=2'
tools.extract_params(url)    # {"a": "1", "b": "2"}
```

#### 10.7.2 extract_url

从url中提取接口

##### 定义

```python
def extract_url(url: str) -> str:
    ...
```

##### 参数

| 参数 | 释义 | 类型 | 是否必选 | 默认值 |
| ---- | ---- | ---- | -------- | ------ |
| url  | url  | str  | 是       | 无     |

##### 返回值

| 释义                | 类型 |
| ------------------- | ---- |
| 截断 query 后的 url | str  |

##### 使用示例

```python
from AioSpider import tools

url = 'http://127.0.0.1:5025/ip?a=1&b=2'
tools.extract_url(url)    # 'http://127.0.0.1:5025/ip'
```

#### 10.7.3 format_cookies

格式化 cookies

##### 定义

```python
def format_cookies(cookies: str) -> dict:
    ...
```

##### 参数

| 参数    | 释义                                              | 类型 | 是否必选 | 默认值 |
| ------- | ------------------------------------------------- | ---- | -------- | ------ |
| cookies | cookies文本字符串，可以是浏览器请求头中复制出来的 | str  | 否       | 无     |

##### 返回值

| 释义                 | 类型 |
| -------------------- | ---- |
| 返回格式化的 cookies | dict |

##### 使用示例

```python
from AioSpider import tools

tools.format_cookies('a=1;b=2')    		     # {'a': '1', 'b': '2'}
tools.format_cookies('a=1;b=2;')    		 # {'a': '1', 'b': '2'}
```

#### 10.7.4 open_html

用默认浏览器打开网址或文件

##### 定义

```python
def open_html(url: str) -> NoReturn:
    ...
```

##### 参数

| 参数 | 释义                 | 类型 | 是否必选 | 默认值 |
| ---- | -------------------- | ---- | -------- | ------ |
| url  | url 或 html 文件路径 | str  | 是       | 无     |

##### 返回值

| 释义 | 类型 |
| ---- | ---- |
| 无   | None |

##### 使用示例

```python
from AioSpider import tools

tools.open_html('https://www.baidu.com')    # 将会用默认浏览器打开
tools.open_html('D:\\a\\b.html')            # 将会用默认浏览器打开
```

#### 10.7.5 quote_params

转换并压缩 params 参数

##### 定义

```python
def quote_params(params: dict) -> str:
    ...
```

##### 参数

| 参数   | 释义       | 类型 | 是否必选 | 默认值 |
| ------ | ---------- | ---- | -------- | ------ |
| params | 待转换数据 | dict | 是       | 无     |

##### 返回值

| 释义                        | 类型 |
| --------------------------- | ---- |
| 转换后可拼接到 url 的字符串 | str  |

##### 使用示例

```python
from AioSpider import tools

tools.quote_params({'a': 1, 'b': 2})    	# 'a=1&b=2'
```

#### 10.7.6 quote_url

拼接 params 参数到 url

##### 定义

```python
def quote_url(url: str, params: dict) -> str:
    ...
```

##### 参数

| 参数   | 释义       | 类型 | 是否必选 | 默认值 |
| ------ | ---------- | ---- | -------- | ------ |
| url    | url        | str  | 是       | 无     |
| params | 待转换数据 | dict | 是       | 无     |

##### 返回值

| 释义       | 类型 |
| ---------- | ---- |
| 拼接的 url | str  |

##### 使用示例

```python
from AioSpider import tools

tools.quote_url('http://127.0.0.1', {'a': 1, 'b': 2})    	# 'http://127.0.0.1?a=1&b=2'
```

### 10.8 爬虫常用工具

#### 10.8.1 parse_json

字典取值


##### 定义

```python
def parse_json(json_data: dict, index: str, default: Any = None, callback: Callable = None) -> Any:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 | 默认值 |
| ----- | ------------ | -------- | -------- | -------- |
| json_data  | 原始数据 |  dict     | 是     | 无 |
| index  | 取值索引 |  str     | 是  | 无 |
| default  | 默认值 |  Any     | 否     |    None    |
| callback | 回调函数 | Callable | 否 | None |

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| 从 json_data 中取到的值 | Any |

##### 使用示例

```python
from AioSpider import tools

data = {
    "a": "null", "b": "false", "f": {
        "h": [
            {"g": "hello"}
        ]
    }
    "c": [{"d": 1}]
}

# 取 false
tools.parse_json(json_data=data, index='b') 
# 取 hello
tools.parse_json(json_data=data, index='f.h[0].g')
tools.parse_json(json_data=data, index='f.h[0].x', default='world')  # world   index索引表达式错误会返回默认值
# 取 {"d": 1}
tools.parse_json(json_data=data, index='c[0]', default={})
```


#### 10.8.2 load_json

将 json 字符串转化为字典

##### 定义

```python
def load_json(string: str, default: Any = None) -> Union[dict, list]:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 | 默认值 |
| ----- | ------------ | -------- | -------- | -------- |
| string  | json 字符串 |  dict     | 是     | 无 |
| default  | 默认值 |    Any   | 否  |    None    |

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| 提取出的字典 | Union[dict, list] |

##### 使用示例

```python
from AioSpider import tools

tools.load_json('{"a": "None", "b": "False"}')    # {'a': 'None', 'b': 'False'}
```

#### 10.8.3 dump_json

将字典转化为 json 字符串

##### 定义

```python
def dump_json(data: dict, separators: tuple = None, *args, **kwargs) -> str:
    ...
```

##### 参数

| 参数       | 释义                                                         | 类型  | 是否必选 | 默认值 |
| ---------- | ------------------------------------------------------------ | ----- | -------- | ------ |
| data       | 原始数据                                                     | dict  | 是       | 无     |
| separators | 分隔符，为了获得最紧凑的JSON表示，指定为 ('，'，'：') 以消除空白。             如果指定，应指定为（item_separator，key_separator）元组 | tuple | 否       | None   |

##### 返回值

| 释义        | 类型 |
| ----------- | ---- |
| json 字符串 | str  |

##### 使用示例

```python
from AioSpider import tools

tools.dump_json({"a": "None", "b": "False"})    						# {'a': 'None', 'b': 'False'}
tools.dump_json({"a": "None", "b": "False"}, separators=('，'，'：')       # {'a':'None','b':'False'}
```

#### 10.8.4 type_converter

类型转换


##### 定义

```python
def type_converter(data: Any, to: Callable = None, force: bool = False) -> Any:
    ...
```

##### 参数

| 参数  | 释义         | 类型     | 是否必选 | 默认值 |
| ----- | ------------ | -------- | -------- | -------- |
| data  | 待转数据 |  Any  | 是     | 无 |
| to  | 转换类型 |    Callable   | 否  |    None    |
| force  | 是否强制转换 |    bool   | 否  |    None    |

##### 返回值

| 释义       | 类型             |
| ---------- | ---------------- |
| 转换值 | Any |

##### 使用示例

```python
from AioSpider import tools

tools.type_converter(100.0, to=int)    # 100
```

#### 10.8.5 deepcopy

深拷贝

##### 定义

```python
def deepcopy(item: Any) -> Any:
    ...
```

##### 参数

| 参数 | 释义       | 类型 | 是否必选 | 默认值 |
| ---- | ---------- | ---- | -------- | ------ |
| item | 待拷贝数据 | Any  | 是       | 无     |

##### 返回值

| 释义       | 类型 |
| ---------- | ---- |
| 深拷贝数据 | Any  |

##### 使用示例

```python
from AioSpider import tools

tools.deepcopy([1, 2, 3])    # [1, 2, 3]
```
