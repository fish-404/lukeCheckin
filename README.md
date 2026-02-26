这是一个 Luke Acdamy 自动签到的工具，可以做到每天自动签到领爱心，并且如果你配置了企业微信的 webhook，可以发送一条签到成功的消息提醒到你的企业微信中。

本工具的用法：
1. Fork 仓库
2. 配置 secret:
   * LUKE_EMAIL：你的 Luke 登录邮箱
   * LUKE_PASSWORD：你的 Luke 登录密码
   * WEWORK_ROBOT_WEBHOOK：企业微信机器人 webhook 地址（你可以创建一个只有你自己的企业，然后发送消息）

本仓库配置了 Action，会每天自动运行签到流程。
