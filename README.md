# 开放api

## 获取地图

### 描述

这个API端点用于生成地图数据。它接受一个序列号和可选的地图大小参数,然后返回生成的地图数据,包括结果地图、路径地图和中间墙壁信息。

### 请求

- **URL**: `/api/getMap`
- **方法**: POST
- **内容类型**: application/json

#### 请求体参数

| 参数名        | 类型    | 必填 | 描述                     |
| ------------- | ------- | ---- | ------------------------ |
| serial_number | integer | 是   | 用于生成地图的序列号     |
| size          | array   | 否   | 地图大小,默认为 [20, 20] |

#### 请求示例

```
{
  "serial_number": 1,
  "size": [25, 25]
}
```

### 响应

#### 响应体

| 字段名      | 类型  | 描述           |
| ----------- | ----- | -------------- |
| result_map  | array | 生成的结果地图 |
| path_map    | array | 生成的路径地图 |
| middle_wall | array | 中间墙壁信息   |

#### 响应示例

```
copy{
  "result_map": [[...], [...], ...],
  "path_map": [[...], [...], ...],
  "middle_wall": [[...], [...], ...]
}
```

## 获取排行榜

获取指定关卡和难度（可选）的排行榜数据。

### 请求

- 方法: `POST`
- URL: `/leaderboard`
- 内容类型: `application/json`

### 请求体

```
copy{
  "level_id": integer,
  "difficulty": integer (可选)
}
```

| 字段         | 类型 | 描述                                                         |
| ------------ | ---- | ------------------------------------------------------------ |
| `level_id`   | 整数 | 必填。要获取排行榜的关卡 ID。                                |
| `difficulty` | 整数 | 可选。指定难度级别进行过滤。如果不提供，将返回所有难度的排行榜。 |

### 响应

#### 成功响应

- 状态码: `200 OK`
- 内容类型: `application/json`

```
copy{
  "关卡": integer,
  "难度": integer 或 null,
  "排行榜": [
    {
      "排名": integer,
      "用户名": string,
      "完成时间": float,
      "难度": integer,
      "时间戳": string
    },
    ...
  ]
}
```

| 字段       | 类型         | 描述                                  |
| ---------- | ------------ | ------------------------------------- |
| `关卡`     | 整数         | 请求的关卡 ID。                       |
| `难度`     | 整数 或 null | 请求的难度级别，如果未指定则为 null。 |
| `排行榜`   | 数组         | 包含排行榜条目的数组。                |
| `排名`     | 整数         | 玩家在此关卡的排名。                  |
| `用户名`   | 字符串       | 玩家的用户名。                        |
| `完成时间` | 浮点数       | 玩家完成关卡的时间（单位可能是秒）。  |
| `难度`     | 整数         | 该记录的难度级别。                    |
| `时间戳`   | 字符串       | ISO 8601 格式的记录创建时间。         |

#### 无数据响应

当指定的关卡和难度组合没有排行榜数据时，API 仍会返回 200 状态码，但会包含一个说明性消息：

```
copy{
  "关卡": integer,
  "难度": integer 或 null,
  "消息": string,
  "排行榜": []
}
```

#### 错误响应

- 状态码: `400 Bad Request`
- 内容类型: `application/json`

```
copy{
  "错误": string
}
```

当请求中缺少必要的 `level_id` 时，将返回此错误响应。

# 认证 API 文档

## 注册

注册新用户。

- **URL**: `/api/register`

- **方法**: `POST`

- 请求体

  :

  ```
  {
    "username": "string",
    "password": "string"
  }
  ```

- 成功响应

  :

  - **状态码**: 201

  - 响应体

    :

    ```
    copy{
      "message": "User registered successfully"
    }
    ```

- 错误响应

  :

  - **状态码**: 400

  - 响应体

    :

    ```
    copy{
      "message": "Username and password are required"
    }
    ```

  或

  ```
  copy{
    "message": "Username already exists"
  }
  ```

## 登录

用户登录并获取访问令牌。

- **URL**: `/api/login`

- **方法**: `POST`

- 请求体

  :

  ```
  copy{
    "username": "string",
    "password": "string"
  }
  ```

- 成功响应

  :

  - **状态码**: 200

  - 响应体

    :

    ```
    copy{
      "access_token": "string"
    }
    ```

- 错误响应

  :

  - **状态码**: 400

  - 响应体

    :

    ```
    copy{
      "message": "Username and password are required"
    }
    ```

  或

  - **状态码**: 401

  - 响应体

    :

    ```
    copy{
      "message": "Invalid username or password"
    }
    ```

# 受保护的资源

## 获取用户游戏记录

获取当前用户的所有游戏记录。

- **URL**: `/api/protected`
- **方法**: GET
- **认证**: 需要JWT令牌

### 响应

#### 成功响应

- **状态码**: 200 OK

- 内容

  :

  ```
  {
    "用户名": "string",
    "游戏记录": [
      {
        "关卡": "string",
        "完成时间": "number",
        "得分": "number",
        "时间戳": "string (ISO 8601 格式)"
      }
    ]
  }
  ```

#### 无记录响应

- **状态码**: 200 OK

- 内容

  :

  ```
  {
    "用户名": "string",
    "游戏记录": [],
    "消息": "该用户还没有游戏记录"
  }
  ```

#### 错误响应

- **状态码**: 404 Not Found

- 内容

  :

  ```
  {
    "错误": "用户不存在"
  }
  ```

## 获取特定关卡的游戏记录

获取当前用户在特定关卡的所有游戏记录。

- **URL**: `/api/level_record`

- **方法**: POST

- **认证**: 需要JWT令牌

- 请求体

  :

  ```
  {
    "level_id": "string"
  }
  ```

### 响应

#### 成功响应

- **状态码**: 200 OK

- 内容

  :

  ```
  {
    "用户名": "string",
    "关卡": "string",
    "游戏记录": [
      {
        "完成时间": "number",
        "得分": "number",
        "时间戳": "string (ISO 8601 格式)"
      }
    ]
  }
  ```

#### 无记录响应

- **状态码**: 200 OK

- 内容

  :

  ```
  copy{
    "用户名": "string",
    "关卡": "string",
    "游戏记录": [],
    "消息": "该用户在关卡 {level_id} 还没有游戏记录"
  }
  ```

#### 错误响应

- **状态码**: 400 Bad Request

- **内容**:

  ```
  copy{
    "错误": "缺少关卡ID"
  }
  ```

- **状态码**: 404 Not Found

- **内容**:

  ```
  copy{
    "错误": "用户不存在"
  }
  ```

## 添加游戏记录 API

### 接口信息

- URL: `/api/add_record`
- 方法: POST
- 需要认证: 是 (JWT Token)

### 请求体

```json
{
  "level_id": 整数,
  "completion_time": 浮点数,
  "score": 整数,
  "difficulty": 整数
}
```

### 参数说明

- `level_id`: 必需。游戏关卡的唯一标识符。
- `completion_time`: 必需。完成关卡所用的时间（以秒为单位）。
- `score`: 必需。在关卡中获得的分数。
- `difficulty_coefficient`: 必需。关卡的难度系数，用于分类排行榜。

### 响应

#### 成功响应

- 状态码: 201 Created
- 内容类型: application/json

```
copy{
  "消息": "游戏记录添加成功，排行榜已更新",
  "记录": {
    "用户名": 字符串,
    "关卡": 整数,
    "完成时间": 浮点数,
    "得分": 整数,
    "难度系数": 浮点数,
    "时间戳": 字符串 (ISO 8601 格式)
  }
}
```

#### 错误响应

- 状态码: 400 Bad Request
  - 原因: 请求体缺少必要的信息

```
{
  "错误": "缺少必要的信息"
}
```

- 状态码: 404 Not Found
  - 原因: 用户不存在

```
{
  "错误": "用户不存在"
}
```

## 检查会话有效性

### 端点

```
GET /api/check_session
```

### 描述

此API用于检查当前用户的会话是否有效。它验证JWT令牌中的会话ID是否与数据库中存储的用户会话ID匹配。

### 认证

需要有效的JWT令牌。

### 请求

#### 头部

- `Authorization`: Bearer <JWT_TOKEN>

#### 参数

无

### 响应

#### 成功响应

**状态码:** 200 OK

```json
{
  "message": "会话有效",
  "valid": true
}
