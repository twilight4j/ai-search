from typing import List, TypeVar, Generic, Dict, Any

T = TypeVar('T')

class PaginationService:
    @staticmethod
    def paginate(items: List[T], page: int, page_size: int) -> Dict[str, Any]:
        """
        주어진 아이템 리스트를 페이지네이션 처리합니다.
        
        Args:
            items: 페이지네이션할 아이템 리스트
            page: 현재 페이지 번호 (1부터 시작)
            page_size: 페이지당 아이템 수
            
        Returns:
            Dict[str, Any]: 페이지네이션 정보와 현재 페이지의 아이템을 포함하는 딕셔너리
            {
                'items': List[T],  # 현재 페이지의 아이템
                'total_count': int,  # 전체 아이템 수
                'total_pages': int,  # 전체 페이지 수
                'current_page': int,  # 현재 페이지
                'page_size': int  # 페이지당 아이템 수
            }
        """
        total_count = len(items)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        total_pages = (total_count + page_size - 1) // page_size  # 올림 나눗셈
        
        return {
            'items': items[start_idx:end_idx],
            'total_count': total_count,
            'total_pages': total_pages,
            'current_page': page,
            'page_size': page_size
        } 