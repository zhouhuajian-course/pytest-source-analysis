# pytest 源码分析

## pytest.main()

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
