export const CATEGORY_IDS = [
  'ai-engineering',
  'system',
  'trend',
  'law',
  'study',
] as const;

export type CategoryId = (typeof CATEGORY_IDS)[number];

export interface CategoryMeta {
  id: CategoryId;
  order: 1 | 2 | 3 | 4 | 5;
  label: string;
  description: string;
  emptyMessage: string;
  reserved?: boolean;
}

export const CATEGORIES: readonly CategoryMeta[] = [
  {
    id: 'ai-engineering',
    order: 1,
    label: '(1) AI Engineering',
    description:
      'LLM 파이프라인, 컨텍스트 엔지니어링, 에이전트 가드레일과 평가 설계를 다룹니다.',
    emptyMessage: '이 카테고리에 아직 등록된 글이 없습니다.',
  },
  {
    id: 'system',
    order: 2,
    label: '(2) System',
    description:
      '의사결정 모델링, 비동기 체결 아키텍처, 데이터 기반 시스템 설계를 다룹니다.',
    emptyMessage: '이 카테고리에 아직 등록된 글이 없습니다.',
  },
  {
    id: 'trend',
    order: 3,
    label: '(3) Trend',
    description:
      '로컬·오픈소스 생태계에서 포착한 일자별 AI 및 개발 기술 트렌드와 실무 적용 해설입니다.',
    emptyMessage: '이 카테고리에 아직 등록된 글이 없습니다.',
  },
  {
    id: 'law',
    order: 4,
    label: '(4) Law',
    description:
      '법률 도메인 상태 머신, 권리 구제 타임라인, 계약 리스크 분석을 다룹니다.',
    emptyMessage: '이 카테고리에 아직 등록된 글이 없습니다.',
  },
  {
    id: 'study',
    order: 5,
    label: '(5) Study',
    description:
      '추후 논문 및 전문 학술 자료 학습 내용을 아카이빙하기 위해 예약된 카테고리입니다.',
    emptyMessage:
      '아직 등록된 글이 없습니다. 추후 논문 및 전문 학술 자료 아카이빙을 위해 비워 둔 예약 카테고리입니다.',
    reserved: true,
  },
] as const;

export const CATEGORY_MAP: Record<CategoryId, CategoryMeta> = Object.fromEntries(
  CATEGORIES.map((category) => [category.id, category])
) as Record<CategoryId, CategoryMeta>;

export function isCategoryId(value: string): value is CategoryId {
  return (CATEGORY_IDS as readonly string[]).includes(value);
}
