
def pops(lst: list, indexes: list[int]) -> None:
	"""
	複数の要素を安全に削除します。渡されたリストに対して破壊的処理を行うメゾットです。
	:param lst: 対象のリスト
	:param indexes: 削除する要素のインデックスのリスト
	"""
	sorted_indexes = sorted(indexes)
	sorted_indexes.reverse()
	for i in sorted_indexes:
		lst.pop(i)
