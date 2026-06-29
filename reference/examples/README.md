# reference/examples/ — 골드스탠다드 예시

"이렇게 만들어줘"의 기준이 되는 **잘 나온 완성 덱**과 그 storyboard를 모은다.
새 문서 작성 시 에이전트가 톤·구성·레이아웃을 참고(few-shot)한다.

권장 구성(예시 1건당):
```
examples/<예시명>/
├── storyboard/      # 그 덱의 슬라이드별 .md (작성 방식 참고용)
└── <예시명>.pdf     # 완성 결과물(렌더 확인용)
```

> 완성 pptx는 `output/` 규칙과 무관하게 **참고용으로 추적**한다(`.gitignore`에서
> `reference/examples/` 아래는 output 제외 규칙의 영향을 받지 않음).
