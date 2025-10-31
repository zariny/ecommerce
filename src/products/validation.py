from __future__ import annotations
from typing import List, Set
from .exceptions import CycleInheritanceError


ProductClass = ...


def validate_no_cycles(base_product_kls: ProductClass, sub_product_kls: ProductClass) -> None:

    visited = set()

    def dfs(product_kls: ProductClass, path: Set) -> None:
        if product_kls.pk in path:
            raise CycleInheritanceError(product_kls)
        if product_kls.pk in visited:
            return
        visited.add(product_kls.pk)
        path.add(product_kls.pk)
        for base in _bases_list(product_kls, base_product_kls, sub_product_kls):
            dfs(base, path)
        path.remove(product_kls.pk)

    dfs(sub_product_kls, set())


def _bases_list(kls: ProductClass, base_product_kls: ProductClass, sub_product_kls: ProductClass) -> List[ProductClass]:

    result = []
    if kls.pk:
        result += list(kls.bases.all()) # TODO: Not optimal
        if kls.pk == sub_product_kls.pk:
            result.append(base_product_kls)
    else:
        result.append(base_product_kls)
    return result
