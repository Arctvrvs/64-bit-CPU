class SmepSmapCheck:
    """Python model for SMEP/SMAP permission checking."""

    def smep_fault(self, is_kernel: bool, va_user: bool, smep: bool) -> bool:
        return bool(is_kernel and smep and va_user)

    def smap_fault(self, is_kernel: bool, va_user: bool, smap: bool, override: bool = False) -> bool:
        return bool(is_kernel and smap and va_user and not override)

    def check(self, is_kernel: bool, va_user: bool, is_exec: bool, smep: bool, smap: bool, override: bool = False) -> bool:
        if is_exec:
            return self.smep_fault(is_kernel, va_user, smep)
        return self.smap_fault(is_kernel, va_user, smap, override)
