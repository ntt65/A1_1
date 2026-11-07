# 평가 기술 발표자료

[기술 발표 PPT](a1_1_eval_technical_final.pptx)는 16:9, 한국어 31장이다. [평가 원문](../a1_1_eval.md)의 필수 질문 19개를 원문 순서대로 번호 매기고 각 질문에 최소 한 장을 배정했다. 보너스 3개는 실제 구현·검증한 결과를 B-1~B-3으로 설명한다. 원본 실행 표·ID·상품 사진·차트는 유지한다.

## 질문별 슬라이드

| 질문 번호 | 슬라이드 | 기술 설명 |
| --- | ---: | --- |
| 1-1 | 3 | 클래스 상태·필수 메서드·반환과 부작용 |
| 1-2 | 4 | 새 커널·20개 테스트·독립 환경 재현 |
| 1-3 | 5 | 거래8,084행·조인9열·자료형·분석 단위 |
| 1-4 | 6~7 | 이미지 축·Mean/Std 수식·상품 매핑·텍스트·원본 사진 |
| 1-5 | 8 | IQR 전후 실제 박스플롯·원금액 보존 |
| 1-6 | 9~10 | 필수6차트의 분석 단위·제목·축·월별 합계 |
| 1-7 | 11~12 | 기술통계·상관2쌍·유효n·해석 |
| 1-8 | 13~14 | RFM4그룹·프로파일·인사이트3개 |
| 2-1 | 15 | 노트북·클래스·공용 함수 책임 |
| 2-2 | 16 | 실제 NumPy 벡터 연산 코드·파일/배치 반복 |
| 2-3 | 17 | 인자 설계·구매일/주문 모드·다른 데이터셋 |
| 2-4 | 18 | 단계별 의사결정·수치 근거·한계 |
| 3-1 | 19 | IQR 손계산·경계·왜도·혼합분포 |
| 3-2 | 20 | 대치20/30/50·관측값 보존·분산 축소 |
| 3-3 | 21~22 | RFM 손계산·평균 순위·동점·분류 우선순위 |
| 3-4 | 23 | 실제배치5×32×32×3·Stride·60KiB·SIMD |
| 4-1 | 24 | 고해상도 I/O·디코딩·배치 메모리·확장 |
| 4-2 | 25 | VIP 유지 실험·대조군·KPI·리스크 |
| 4-3 | 26 | T이전 피처·미래30일 타겟·누수·관측 중단 |
| B-1 | 27 | 실제8구간 히스토그램·엣지·2×2 알려진 입력 |
| B-2 | 28 | 실제 코호트550/288/162·분모·미래NaN |
| B-3 | 29 | 실제1000고객 Plotly·회전·범례·원본ID hover |
| 시연·출처 | 30~31 | 복사 실행 명령·검증 증거·학습 자료 |

1쪽은 표지, 2쪽은 항목별 위치 안내다. 각 장의 발표자 노트에는 질문 원문, 설명할 내용, 코드·화면 시연, 예상 꼬리 질문과 SRC·출처가 있다. 발표 연습은 **질문 번호 → 원리와 수식 → SRC → 실제 실행 증거 → 한계** 순서로 한다.

## 구성과 근거

- 표17개와 추가 데이터 차트3개, 처리 흐름·배열 축·메모리·실험·시간 구간 도식은 PowerPoint에서 편집할 수 있다. 원본 노트북의 사진·6종 차트와 실제 Plotly 화면은 실행 증거 이미지로 그대로 넣었다.
- 숫자는 [실제 분석 JSON](../results/analysis_aggregates.json), 그림은 [필수 차트](../results/analysis_report.md)와 [보너스 결과](../results/bonus/cohort_retention.csv), 원본 사진은 [실행 노트북](../../notebooks/analysis_report.ipynb)에서 가져온다.
- Excel 편집 차트의 수치 정밀도에 맞춰 차트 내부 값은 최대12유효숫자로 표현한다. 원본 계산 JSON은 변경하지 않으며 슬라이드의 표시 자릿수에 영향을 주지 않는다.
- 캠페인·예측 모델은 평가 질문에 대한 설계안이다. 실제 캠페인 성과·모델 학습을 수행했다고 주장하지 않는다. 코호트는 가입일 자료가 없어 첫 관찰 구매월 기준이다.
- 원본 평가 PDF·Markdown은 수정하지 않았다. NumPy의 [배열 stride](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.strides.html), [SIMD](https://numpy.org/doc/stable/reference/simd/index.html), [std](https://numpy.org/doc/stable/reference/generated/numpy.std.html), Pandas의 [평균 순위](https://pandas.pydata.org/docs/reference/api/pandas.Series.rank.html)를 관련 장의 노트에서 연결한다.

자세한 용어는 [기술 학습서](../tech_study.md), 구술 연습은 [평가 Q&A](../a1_1_evaluation_qa.md), 전체 실행은 [저장소 README](../../README.md)에 있다.

## 작성 코드와 재생성

SRC: [작성 도구](../../utils/build_eval_presentation.mjs), [질문별 원고](../../utils/eval_presentation_content.mjs). 분석용 Python 의존성에 발표 도구를 추가하지 않고 Codex의 번들 Node.js·Artifact Tool·검증 도구를 사용한다. 다음은 현재 PC의 경로이며 다른 환경에서는 번들 위치에 맞춰 바꾼다.

```powershell
$artifactNode = "C:/Users/4cat1/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe"
$artifactModules = "C:/Users/4cat1/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules"
$slideSkill = "C:/Users/4cat1/.codex/plugins/cache/openai-primary-runtime/presentations/26.1105.12137/skills/presentations"
$artifactPython = "C:/Users/4cat1/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe"
& $artifactNode utils/build_eval_presentation.mjs --modules $artifactModules --skill-dir $slideSkill --python $artifactPython --output docs/presentation/a1_1_eval_technical_revision.pptx
```

출력 파일은 기존 파일을 덮어쓰지 않으므로 개정할 때 새 이름을 지정한다. 임시 PPT·질문 매핑 JSON·슬라이드 PNG·최종 파일 검증 기록은 Git 제외 `data/presentation-build/`에 남는다. `.chart-data-*`도 Git 제외인 임시 차트 변환 작업 폴더다. 빌드는 19개 질문 누락, native 표·차트, 글꼴·페이지 크기·파일 구조를 검사하고 최종 PPT를 다시 읽어 모든 장을 렌더링한다. 실제 수치·설정이 바뀌면 원고의 해석·손계산·설명도 함께 검토한다. 생성된 최종 파일은 전체 장을 육안으로 확인한 뒤 제출한다.

관련 작업: [발표자료 이슈 #17](https://github.com/ntt65/A1_1/issues/17). 보너스 실제 구현은 [별도 이슈 #18](https://github.com/ntt65/A1_1/issues/18)에서 완료했다.
