# Linux PAM Integration

FaceLock integrates with Linux through the PAM (`pam_exec`) module.

The authentication flow is:

```
Plasma Login
      │
      ▼
Linux PAM
      │
      ▼
pam_exec.so
      │
      ▼
facelock verify
      │
      ▼
Exit Code
```

A successful authentication returns exit code `0`.

A failed authentication returns a non-zero exit code, allowing PAM to continue with password authentication.

The files in this directory are examples only and should be adapted to match the target system.