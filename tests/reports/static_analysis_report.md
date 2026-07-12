# Static Code Analysis Report

Generated at: 2026-07-09 22:19:44

## 1. Flake8 Syntax Checks
**Exit Code**: 0
```text
0

```

## 2. Pylint Error Checks
**Exit Code**: 0
```text

--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)


```

## 3. Mypy Type Consistency
**Exit Code**: 0
```text
Success: no issues found in 193 source files

```

## 4. Radon Complexity Grade
**Exit Code**: 0
```text
backend\app\main.py
    F 46:0 lifespan - B (6)
    F 129:0 root - A (1)
backend\app\auth\jwt_service.py
    C 12:0 JWTService - A (4)
    M 42:4 JWTService.decode_token - A (4)
    M 14:4 JWTService.create_access_token - A (2)
    M 28:4 JWTService.create_refresh_token - A (2)
backend\app\auth\models.py
    C 5:0 RefreshToken - A (1)
backend\app\auth\password_service.py
    C 3:0 PasswordService - A (3)
    M 14:4 PasswordService.verify_password - A (2)
    M 5:4 PasswordService.hash_password - A (1)
backend\app\auth\repository.py
    C 5:0 RefreshTokenRepository - A (2)
    M 6:4 RefreshTokenRepository.__init__ - A (1)
    M 9:4 RefreshTokenRepository.create - A (1)
    M 16:4 RefreshTokenRepository.get_by_hash - A (1)
    M 22:4 RefreshTokenRepository.revoke - A (1)
    M 29:4 RefreshTokenRepository.revoke_all_for_user - A (1)
    M 36:4 RefreshTokenRepository.get_all_for_user - A (1)
backend\app\auth\routes.py
    F 38:0 login - A (2)
    F 59:0 logout - A (2)
    F 76:0 refresh - ...
```
