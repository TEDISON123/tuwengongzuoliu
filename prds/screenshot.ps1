$ErrorActionPreference = "Stop"
$OutputDir = "D:\cadabra_tools003\AgentPro\tuwengongzuoliu\prds\screenshots"
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null

$EdgeExe = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# 待截图目标列表（绝对路径，宽，高）
$Targets = @(
    @{ Name = "01_page1_cover";        Path = "D:\cadabra_tools003\AgentPro\tuwengongzuoliu\examples\mortgage_vs_invest\page_1.html";                W = 540; H = 720 },
    @{ Name = "02_page2_painpoint";    Path = "D:\cadabra_tools003\AgentPro\tuwengongzuoliu\examples\mortgage_vs_invest\page_2.html";                W = 540; H = 720 },
    @{ Name = "03_page3_contrast";     Path = "D:\cadabra_tools003\AgentPro\tuwengongzuoliu\examples\mortgage_vs_invest\page_3.html";                W = 540; H = 720 },
    @{ Name = "04_page4_sideA";        Path = "D:\cadabra_tools003\AgentPro\tuwengongzuoliu\examples\mortgage_vs_invest\page_4.html";                W = 540; H = 720 },
    @{ Name = "05_page5_sideB";        Path = "D:\cadabra_tools003\AgentPro\tuwengongzuoliu\examples\mortgage_vs_invest\page_5.html";                W = 540; H = 720 },
    @{ Name = "06_page6_hook";         Path = "D:\cadabra_tools003\AgentPro\tuwengongzuoliu\examples\mortgage_vs_invest\page_6.html";                W = 540; H = 720 },
    @{ Name = "07_all_pages_viewer";   Path = "D:\cadabra_tools003\AgentPro\tuwengongzuoliu\examples\mortgage_vs_invest\all_pages_viewer.html";      W = 1440; H = 2000 },
    @{ Name = "08_pipeline_controller";Path = "D:\cadabra_tools003\AgentPro\tuwengongzuoliu\templates\pipeline_controller.html";                    W = 1280; H = 900 },
    @{ Name = "09_incentive_calc";     Path = "D:\cadabra_tools003\AgentPro\tuwengongzuoliu\templates\incentive_calculator.html";                  W = 1280; H = 900 },
    @{ Name = "10_finance_graph";      Path = "D:\cadabra_tools003\AgentPro\tuwengongzuoliu\templates\finance_graph_explorer.html";                W = 1280; H = 900 }
)

foreach ($t in $Targets) {
    $png = Join-Path $OutputDir "$($t.Name).png"
    Write-Host "[Shot] $($t.Name) -> $png"
    $uri = "file:///" + $t.Path.Replace("\", "/")
    # 删除已存在截图
    if (Test-Path $png) { Remove-Item $png -Force }
    $proc = Start-Process -FilePath $EdgeExe -ArgumentList @(
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        "--virtual-time-budget=8000",
        "--window-size=$($t.W),$($t.H)",
        "--screenshot=`"$png`"",
        "`"$uri`""
    ) -PassThru -Wait -WindowStyle Hidden
}
Write-Host "All done."
