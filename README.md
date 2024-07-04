# pytest 源码分析

https://github.com/pytest-dev/pytest  
https://github.com/pytest-dev/pluggy

pytest 功能非常多，本质是一个个插件组成的功能，插件由 pluggy 进行管理  
pluggy是一个插件系统，用于pytest插件的管理和钩子调用  
pluggy使pytest由钩子功能，实现主程序与插件连接

1. configuration
2. collection
3. running
4. reporting

## hook functions

https://docs.pytest.org/en/8.2.x/how-to/writing_hook_functions.html#writinghooks

## plugins

https://docs.pytest.org/en/8.2.x/how-to/plugins.html  
https://docs.pytest.org/en/8.2.x/how-to/writing_plugins.html

```
builtin plugins: loaded from pytest’s internal _pytest directory.
external plugins: modules discovered through setuptools entry points
conftest.py plugins: modules auto-discovered in test directories
```

```
pytest --trace-config 可以查看 插件具体位置
```

## fixture

https://docs.pytest.org/en/8.2.x/how-to/fixtures.html

使用debug的方式 追踪Fixture的原理

```python
# D:\Python\Python3.12\Lib\site-packages\_pytest\python.py
@hookimpl(trylast=True)
def pytest_pyfunc_call(pyfuncitem: "Function") -> Optional[object]:
    testfunction = pyfuncitem.obj
    if is_async_function(testfunction):
        async_warn_and_skip(pyfuncitem.nodeid)
    funcargs = pyfuncitem.funcargs
    # 参数 fixture
    testargs = {arg: funcargs[arg] for arg in pyfuncitem._fixtureinfo.argnames}
    # 调用测试函数 传测试参数
    result = testfunction(**testargs)
    if hasattr(result, "__await__") or hasattr(result, "__aiter__"):
        async_warn_and_skip(pyfuncitem.nodeid)
    elif result is not None:
        warnings.warn(
            PytestReturnNotNoneWarning(
                f"Expected None, but {pyfuncitem.nodeid} returned {result!r}, which will be an error in a "
                "future version of pytest.  Did you mean to use `assert` instead of `return`?"
            )
        )
    return True
```

直接读fixture 不翻译成中文 

```
Fixture scopes

Fixtures are created when first requested by a test, and are destroyed based on their scope:

function: the default scope, the fixture is destroyed at the end of the test.
class: the fixture is destroyed during teardown of the last test in the class.
module: the fixture is destroyed during teardown of the last test in the module.
package: the fixture is destroyed during teardown of the last test in the package where the fixture is defined, including sub-packages and sub-directories within it.
session: the fixture is destroyed at the end of the test session.
```


## conftest的conf的解释

网络上没有比较靠谱的解释

借鉴这个工具的说明，这个工具可能跟pytest没关系

https://www.conftest.dev/

应该是 configuration 的缩写

## 插件发现顺序文档

Plugin discovery order at tool startup

https://docs.pytest.org/en/stable/how-to/writing_plugins.html#plugin-discovery-order-at-tool-startup

## conftest.py文档

https://docs.pytest.org/en/stable/how-to/writing_plugins.html#conftest-py-local-per-directory-plugins

## 插件开发文档

https://docs.pytest.org/en/latest/how-to/writing_plugins.html

比较重要的 setup.py 里面有个 entry_points

## 钩子执行顺序

*来自网络*

https://github.com/pytest-dev/pytest/issues/3261

```
root
└── pytest_cmdline_main
    ├── pytest_plugin_registered
    ├── pytest_configure
    │   └── pytest_plugin_registered
    ├── pytest_sessionstart
    │   ├── pytest_plugin_registered
    │   └── pytest_report_header
    ├── pytest_collection
    │   ├── pytest_collectstart
    │   ├── pytest_make_collect_report
    │   │   ├── pytest_collect_file
    │   │   │   └── pytest_pycollect_makemodule
    │   │   └── pytest_pycollect_makeitem
    │   │       └── pytest_generate_tests
    │   │           └── pytest_make_parametrize_id
    │   ├── pytest_collectreport
    │   ├── pytest_itemcollected
    │   ├── pytest_collection_modifyitems
    │   └── pytest_collection_finish
    │       └── pytest_report_collectionfinish
    ├── pytest_runtestloop
    │   └── pytest_runtest_protocol
    │       ├── pytest_runtest_logstart
    │       ├── pytest_runtest_setup
    │       │   └── pytest_fixture_setup
    │       ├── pytest_runtest_makereport
    │       ├── pytest_runtest_logreport
    │       │   └── pytest_report_teststatus
    │       ├── pytest_runtest_call
    │       │   └── pytest_pyfunc_call
    │       ├── pytest_runtest_teardown
    │       │   └── pytest_fixture_post_finalizer
    │       └── pytest_runtest_logfinish
    ├── pytest_sessionfinish
    │   └── pytest_terminal_summary
    └── pytest_unconfigure
```

## src/_pytest/fixtures.py

fixture 源码实现

https://github.com/pytest-dev/pytest/blob/main/src/_pytest/fixtures.py

## pytest 三种插件

*来自网络*

```
pytest插件通过hook函数来实现，pytest主要包括以下三种插件

    内置插件：pytest内部的_pytest目录中加载：\Lib\site-packages\_pytest\hookspec.py
    外部插件：pip install 插件，通过setuptools的Entry points机制来发现外部插件，可用插件列表：https://docs.pytest.org/en/latest/reference/plugin_list.html
    本地插件：conftest.py插件，pytest自动模块发现机制，在项目根目录下的conftest文件起到全局作用，在项目下的子目录中的conftest.py文件作用范围只能在该层级及以下目录生效。

他们的加载顺序为：

    内置插件
    外部插件
    本地插件
```

## src/_pytest/hookspec.py

https://github.com/pytest-dev/pytest/blob/main/src/_pytest/hookspec.py

src/_pytest/hookspec.py 定义了大量 hook spec 钩子说明 类似接口、类似声明

## PluginManager 

pytest源码中，重要的PluginManager来自pluggy，
这是从旧版本pytest中分离出来的插件管理器

This is the core framework used by the pytest, tox, and devpi projects.  
是pytest的核心框架

## pytest.main() 源码分析

```python
def main(
    # 第一个参数
    args: Optional[Union[List[str], "os.PathLike[str]"]] = None,
    # 第二个参数
    plugins: Optional[Sequence[Union[str, _PluggyPlugin]]] = None,
    # 返回值 退出码
) -> Union[int, ExitCode]:
    # 执行一个在进程 测试 运行
    """Perform an in-process test run.
    # 命令行参数
    :param args: List of command line arguments.
    # 插件列表
    :param plugins: List of plugin objects to be auto-registered during initialization.
    # 退出码
    :returns: An exit code.
    """
    try:
        try:
            config = _prepareconfig(args, plugins)
        # 捕获conftest导入失败    
        except ConftestImportFailure as e:
            exc_info = ExceptionInfo.from_exc_info(e.excinfo)
            # 终端writer
            tw = TerminalWriter(sys.stderr)
            tw.line(f"ImportError while loading conftest '{e.path}'.", red=True)
            # 回溯
            exc_info.traceback = exc_info.traceback.filter(
                filter_traceback_for_conftest_import_failure
            )
            exc_repr = (
                exc_info.getrepr(style="short", chain=False)
                if exc_info.traceback
                else exc_info.exconly()
            )
            formatted_tb = str(exc_repr)
            for line in formatted_tb.splitlines():
                tw.line(line.rstrip(), red=True)
            # 用法错误    
            return ExitCode.USAGE_ERROR
        # 没有错误时，执行代码    
        else:
            try:
                # pytest 命令行 main 参数 配置
                ret: Union[ExitCode, int] = config.hook.pytest_cmdline_main(
                    config=config
                )
                try:
                    # 返回错误码
                    return ExitCode(ret)
                except ValueError:
                    return ret
            # 最后        
            finally:
                # 释放配置
                config._ensure_unconfigure()
    # 捕获用法错误            
    except UsageError as e:
        # 终端writer
        tw = TerminalWriter(sys.stderr)
        # 遍历异常的args
        for msg in e.args:
            tw.line(f"ERROR: {msg}\n", red=True)
        # 返回错误码 用法错误    
        return ExitCode.USAGE_ERROR
```

```python
# 准备配置
def _prepareconfig(
    args: Optional[Union[List[str], "os.PathLike[str]"]] = None,
    plugins: Optional[Sequence[Union[str, _PluggyPlugin]]] = None,
    # 返回配置
) -> "Config":
    # args为None，使用sys.argv[1:]，命令行参数
    if args is None:
        args = sys.argv[1:]
    # os.PathLike时    
    elif isinstance(args, os.PathLike):
        args = [os.fspath(args)]
    # args不是list，抛出类型错误    
    elif not isinstance(args, list):
        msg = (  # type:ignore[unreachable]
            "`args` parameter expected to be a list of strings, got: {!r} (type: {})"
        )
        raise TypeError(msg.format(args, type(args)))
    # 获取配置
    config = get_config(args, plugins)
    # 配置管理器
    pluginmanager = config.pluginmanager
    try:
        # 如果传了插件
        if plugins:
            for plugin in plugins:
                # 字符串
                if isinstance(plugin, str):
                    # 考虑插件
                    pluginmanager.consider_pluginarg(plugin)
                # pluggy 插件    
                else:
                    # 注册插件
                    pluginmanager.register(plugin)
        # 插件管理器 hook 命令行解析            
        config = pluginmanager.hook.pytest_cmdline_parse(
            pluginmanager=pluginmanager, args=args
        )
        # 返回配置
        return config
    # 捕获基础异常    
    except BaseException:
        # unconfigure
        config._ensure_unconfigure()
        # 继续抛出异常
        raise
```

```python

# 获取配置        
def get_config(
    args: Optional[List[str]] = None,
    plugins: Optional[Sequence[Union[str, _PluggyPlugin]]] = None,
) -> "Config":
    # subsequent calls to main will create a fresh instance
    # 创建配置管理器
    pluginmanager = PytestPluginManager()
    # 创建配置
    config = Config(
        pluginmanager,
        invocation_params=Config.InvocationParams(
            # args或者空元祖
            args=args or (),
            plugins=plugins,
            # 当前工作目录
            dir=Path.cwd(),
        ),
    )
    # args不是None
    if args is not None:
        # Handle any "-p no:plugin" args.
        # 处理 -p no:plugin 参数
        pluginmanager.consider_preparse(args, exclude_only=True)
    # 默认插件
    for spec in default_plugins:
        # 导入插件
        pluginmanager.import_plugin(spec)

    return config        
```

```python

# Plugins that cannot be disabled via "-p no:X" currently.
# 必要插件
essential_plugins = (
    # 标记
    "mark",
    "main",
    "runner",
    # 夹具
    "fixtures",
    "helpconfig",  # Provides -p.
)
# 默认插件 = 必要插件 + 其他插件
default_plugins = essential_plugins + (
    "python",
    # 终端
    "terminal",
    "debugging",
    # unittest框架
    "unittest",
    "capture",
    # 跳过
    "skipping",
    "legacypath",
    # 临时目录
    "tmpdir",
    "monkeypatch",
    "recwarn",
    "pastebin",
    # nose框架
    "nose",
    # 断言
    "assertion",
    "junitxml",
    "doctest",
    "cacheprovider",
    "freeze_support",
    "setuponly",
    "setupplan",
    "stepwise",
    "warnings",
    "logging",
    # 报告
    "reports",
    "python_path",
    *(["unraisableexception", "threadexception"] if sys.version_info >= (3, 8) else []),
    "faulthandler",
)

```
