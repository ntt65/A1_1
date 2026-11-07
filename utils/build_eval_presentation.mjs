/**
 * 평가 질문별 기술 PPT를 현재 저장소의 공개 실행 결과로 재생성한다.
 * 런타임·스킬 경로는 CLI로 받고, 임시 렌더/검증 기록은 Git 제외 data/에 둔다.
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
import { evaluationSlides } from './eval_presentation_content.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const options = Object.fromEntries(process.argv.slice(2).reduce((pairs, value, index, all) => {
  if (value.startsWith('--')) pairs.push([value.slice(2), all[index + 1]]);
  return pairs;
}, []));
for (const name of ['modules', 'skill-dir', 'python']) {
  if (!options[name]) throw Error(`Missing --${name}`);
}
const BUILD = path.resolve(ROOT, options.build || 'data/presentation-build');
const FINAL = path.resolve(ROOT, options.output || 'docs/presentation/a1_1_eval_technical_final.pptx');
const requireRuntime = createRequire(path.join(path.resolve(options.modules), 'entry.cjs'));
process.env.RUNTIME_NODE_MODULES = path.resolve(options.modules);
const { Presentation, PresentationFile, FileBlob } = await import(pathToFileURL(requireRuntime.resolve('@oai/artifact-tool')).href);
const { finalizePresentation, applyPresentationChartFont } = await import(pathToFileURL(path.join(options['skill-dir'], 'container_tools/artifact_tool_utils.mjs')).href);
const FONT = 'Malgun Gothic';
const C = { ink: '#102B46', blue: '#176CA1', teal: '#007C83', orange: '#B85925', muted: '#536477', pale: '#EFF5FA', line: '#CAD5DF', white: '#FFFFFF' };
const W = 1600, H = 900;
await fs.mkdir(BUILD, { recursive: true });
await fs.mkdir(path.dirname(FINAL), { recursive: true });
const data = JSON.parse(await fs.readFile(path.join(ROOT, 'docs/results/analysis_aggregates.json'), 'utf8'));
const specifications = evaluationSlides(data);
const evalText = (await fs.readFile(path.join(ROOT, 'docs/a1_1_eval.md'), 'utf8')).replace(/\r\n/g, '\n');
const questions = {};
for (let section = 1; section <= 4; section++) {
  const block = evalText.split(`### 항목 ${section}\n`)[1]?.split(`### 항목 ${section + 1}`)[0];
  if (!block) throw Error('Missing evaluation section ' + section);
  block.split('\n').filter(line => line.startsWith('- ')).forEach((line, i) => questions[`${section}-${i + 1}`] = line.slice(2));
}
if (Object.keys(questions).length !== 19) throw Error('Expected 19 mandatory questions');
for (const id of Object.keys(questions)) {
  if (!specifications.some(slide => slide.id === id)) throw Error('Missing question slide: ' + id);
}
const presentation = Presentation.create({ slideSize: { width: W, height: H } });
const tableOwners = [], chartOwners = [];
let sequence = 0;

/** 지정 영역에 편집 가능한 텍스트를 배치하고 글꼴·여백을 통일한다. */
function text(slide, value, x, y, width, height, size = 28, color = C.ink, bold = false, alignment = 'left') {
  const shape = slide.shapes.add({ geometry: 'textbox', name: `text-${++sequence}`,
    position: { left: x, top: y, width, height }, fill: 'none', line: { fill: 'none', width: 0 } });
  shape.text = value;
  shape.text.style = { typeface: FONT, fontSize: size, color, bold, alignment,
    verticalAlignment: 'top', wrap: 'square', autoFit: 'none', insets: 0 };
  return shape;
}

/** 기술 도식의 실제 데이터 노드를 편집 가능한 도형으로 배치한다. */
function node(slide, value, x, y, width, height, color = C.blue) {
  const shape = slide.shapes.add({ geometry: 'rect', name: `node-${++sequence}`,
    position: { left: x, top: y, width, height }, fill: C.pale, line: { fill: color, width: 2 } });
  shape.text = value;
  shape.text.style = { typeface: FONT, fontSize: 27, color: C.ink, alignment: 'center',
    verticalAlignment: 'middle', wrap: 'square', autoFit: 'none', insets: 12 };
  return shape;
}

/** 도식 노드를 가로 또는 꺾인 연결선으로 연결한다. */
function connect(slide, from, to, elbow = false) {
  return slide.shapes.connect(from, to, { kind: elbow ? 'elbow' : 'straight', fromSide: 'right', toSide: 'left',
    line: { fill: C.muted, width: 2 }, tail: { type: 'arrow', width: 'med', length: 'med' } });
}

/** 같은 순서의 처리 단계를 한 줄의 호출 흐름으로 표현한다. */
function flow(slide, steps, y = 235, height = 140) {
  const gap = 44, width = (1460 - gap * (steps.length - 1)) / steps.length;
  const shapes = steps.map((value, i) => node(slide, value, 70 + i * (width + gap), y, width, height));
  shapes.slice(1).forEach((shape, i) => connect(slide, shapes[i], shape));
}

/** 원고·설명에 필요한 코드를 원문 그대로 편집 가능한 텍스트로 표시한다. */
function code(slide, value, x, y, width, height, size = 25) {
  slide.shapes.add({ geometry: 'rect', position: { left: x, top: y, width, height }, fill: C.ink, line: { fill: 'none', width: 0 } });
  return text(slide, value, x + 24, y + 22, width - 48, height - 44, size, C.white);
}

/** 행·열·수치가 편집 가능한 native PowerPoint 표를 만든다. */
function table(slide, headers, rows, x = 70, y = 225, width = 1460, height = 490, widths = null, size = 26) {
  const values = [headers, ...rows].map(row => row.map(String));
  const result = slide.tables.add({ rows: values.length, columns: headers.length, left: x, top: y, width, height,
    columnWidths: widths || Array(headers.length).fill(width / headers.length), values });
  result.borders.assign({ style: 'solid', fill: C.line, width: 1 });
  for (let r = 0; r < values.length; r++) {
    result.rows[r].height = height / values.length;
    for (let c = 0; c < headers.length; c++) {
      const cell = result.getCell(r, c);
      cell.fill = r === 0 ? C.ink : r % 2 ? C.white : C.pale;
      cell.text.style = { typeface: FONT, fontSize: size, bold: r === 0, color: r === 0 ? C.white : C.ink };
    }
  }
  tableOwners.push(presentation.slides.items.length);
  return result;
}

/** 실제 집계값으로 편집 가능한 차트를 만들고 차트 자체의 글꼴도 지정한다. */
function chart(slide, type, config) {
  // Excel의 15자리 제약 안에서 편집 차트 값을 표현한다. 분석 JSON 원값은 유지한다.
  const series = config.series.map(item => ({ ...item,
    values: item.values.map(value => value == null ? null : Number(Number(value).toPrecision(12))) }));
  const result = slide.charts.add(type, { chartFill: C.white, plotAreaFill: C.white,
    titleTextStyle: { fontSize: 26, fill: C.ink }, ...config, series });
  applyPresentationChartFont(result, { fontFamily: FONT });
  chartOwners.push(presentation.slides.items.length);
  return result;
}

/** 원본 실행 그림의 비율을 유지해 실제 결과 이미지로 넣는다. */
async function picture(slide, filename, x, y, width, height) {
  const bytes = await fs.readFile(filename);
  return slide.images.add({ blob: bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength),
    contentType: 'image/png', alt: path.basename(filename), fit: 'contain',
    position: { left: x, top: y, width, height } });
}

/** 표시 형식만 반올림하고 계산은 입력 집계의 원값을 유지한다. */
const fixed = (value, digits = 6) => Number(value).toFixed(digits);
const percent = value => (Number(value) * 100).toFixed(1) + '%';
const fig = name => path.join(ROOT, 'docs/results/figures', name);
const bonus = name => path.join(ROOT, 'docs/results/bonus', name);
const sourceNotebook = JSON.parse(await fs.readFile(path.join(ROOT, 'notebooks/analysis_report.ipynb'), 'utf8'));
const gallery = sourceNotebook.cells.flatMap(cell => cell.outputs || []).find(output => output.data?.['image/png']);
if (!gallery) throw Error('Original product gallery output missing');
const galleryPath = path.join(BUILD, 'original-product-gallery.png');
await fs.writeFile(galleryPath, Buffer.from(gallery.data['image/png'].join?.('') || gallery.data['image/png'], 'base64'));

for (const [index, spec] of specifications.entries()) {
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  if (spec.kind !== 'cover') {
    text(slide, `${spec.id ? spec.id + '  ' : ''}${spec.title}`, 70, 45, 1460, 66, 44, C.ink, true);
    text(slide, spec.subtitle, 70, 125, 1460, 72, 27, C.muted);
  }
  if (spec.kind === 'cover') {
    text(slide, spec.title, 85, 240, 1430, 120, 72, C.ink, true);
    text(slide, spec.subtitle, 85, 390, 1410, 80, 39, C.blue);
    text(slide, spec.text, 85, 555, 1430, 135, 29, C.muted);
  } else if (spec.kind === 'index') {
    const sections = [1, 2, 3, 4].map(section => {
      const entries = Object.entries(questions).filter(([id]) => id.startsWith(section + '-'));
      const pages = specifications.flatMap((item, i) => item.id?.startsWith(section + '-') ? [i + 1] : []);
      return [`항목 ${section}`, `${entries.length}개 질문`, `${pages[0]}~${pages.at(-1)}쪽`, ['구현·실행·자료·차트·결과', '책임·벡터화·인자·의사결정', 'IQR·대치·RFM·메모리/SIMD', '병목·마케팅 실험·예측 확장'][section - 1]];
    });
    const bonusPages = specifications.flatMap((item, i) => item.id?.startsWith('B-') ? [i + 1] : []);
    table(slide, ['구분', '질문 수', '슬라이드', '기술 설명 범위'], [...sections, ['보너스', '3개 구현', `${bonusPages[0]}~${bonusPages.at(-1)}쪽`, '히스토그램·엣지 / 코호트 / Plotly']], 70, 230, 1460, 490, [220, 240, 260, 740]);
    text(slide, '각 질문의 전체 원문·설명 순서·코드 시연·꼬리 질문·출처는 발표자 노트에 있다.', 70, 755, 1460, 65, 28);
  } else if (spec.kind === 'table') {
    table(slide, spec.headers, spec.rows, 70, 225, 1460, 490, spec.widths);
    text(slide, spec.bottom || '', 70, 755, 1460, 65, 27, C.muted);
  } else if (spec.kind === 'flow') {
    flow(slide, spec.steps);
    text(slide, spec.leftTitle, 70, 440, 690, 48, 32, C.blue, true);
    text(slide, spec.left, 70, 510, 690, 275, 29);
    text(slide, spec.rightTitle, 840, 440, 690, 48, 32, C.teal, true);
    text(slide, spec.right, 840, 510, 690, 275, 29);
  } else if (spec.kind === 'tensor') {
    const dims = ['N\n이미지', 'H=32\n높이', 'W=32\n너비', 'C=3\nRGB'];
    dims.forEach((value, i) => node(slide, value, 70 + i * 185, 240, 160, 115, i ? C.muted : C.blue));
    text(slide, 'axis=(1,2,3)을 축약하면 이미지 번호 N만 남는다', 70, 385, 750, 80, 29, C.blue, true);
    code(slide, spec.code, 70, 490, 850, 245, 25);
    text(slide, spec.text, 995, 255, 535, 420, 30);
    text(slide, spec.bottom, 70, 765, 1460, 56, 26, C.muted);
  } else if (spec.kind === 'gallery') {
    await picture(slide, galleryPath, 70, 215, 930, 565);
    text(slide, spec.text, 1050, 250, 480, 500, 29);
  } else if (spec.kind === 'evidence') {
    if (spec.images.length === 1) {
      await picture(slide, fig(spec.images[0]), 70, 235, 930, 550);
      text(slide, spec.text, 1050, 260, 480, 480, 29);
    } else {
      const count = spec.images.length, width = (1460 - 32 * (count - 1)) / count;
      for (let i = 0; i < count; i++) {
        await picture(slide, fig(spec.images[i]), 70 + i * (width + 32), 235, width, 445);
        text(slide, spec.captions[i], 70 + i * (width + 32), 705, width, 70, 26, C.blue, true, 'center');
      }
      text(slide, spec.bottom, 70, 785, 1460, 44, 25, C.muted);
    }
  } else if (spec.kind === 'statistics') {
    const labels = { price: '거래 금액', prod_name_length: '상품명 문자 수', prod_name_word_count: '상품명 단어 수' };
    const rows = Object.entries(data.statistics).map(([key, value]) => [labels[key], fixed(value.mean), fixed(value.median), fixed(value.std), fixed(value.Q1), fixed(value.Q3)]);
    table(slide, ['변수', '평균', '중앙값', '표준편차', 'Q1', 'Q3'], rows, 70, 250, 1460, 350, [310, 230, 230, 230, 230, 230], 25);
    text(slide, '가격 평균0.025014 > 중앙값0.022017. 오른쪽 꼬리와 함께 해석한다.\n금액은 원본 단위다. 문자·단어 수는 거래에 연결된 피처의 요약이다.', 70, 655, 1460, 140, 30);
  } else if (spec.kind === 'correlations') {
    chart(slide, 'bar', { position: { left: 70, top: 235, width: 850, height: 550 }, title: 'Pearson r',
      categories: ['이미지 mean/std', '고객 F/M'], series: [{ name: 'r', values: data.correlations.map(row => row.pearson), fill: C.blue }],
      hasLegend: false, barOptions: { direction: 'column', grouping: 'clustered', gapWidth: 130 },
      xAxis: { title: '분석 쌍', tickLabelPosition: 'low', textStyle: { fontSize: 23 } },
      yAxis: { title: '상관계수 r', min: -1, max: 1, majorUnit: .5, numberFormatCode: '0.0', textStyle: { fontSize: 23 } },
      dataLabels: { showValue: true, position: 'center', numberFormatCode: '0.000', textStyle: { fontSize: 23, fill: C.white } } });
    text(slide, spec.text, 990, 250, 540, 540, 29);
  } else if (spec.kind === 'segments') {
    const names = ['VIP', 'Churned', 'New', 'Loyal'];
    chart(slide, 'bar', { position: { left: 70, top: 230, width: 850, height: 550 }, title: '고객 비중과 금액 비중', categories: names,
      series: [{ name: '고객 비중', values: names.map(n => data.profile[n].Customer_share), fill: C.blue },
               { name: '금액 비중', values: names.map(n => data.profile[n].Monetary_share), fill: C.teal }],
      barOptions: { direction: 'column', grouping: 'clustered', gapWidth: 100 }, hasLegend: true,
      legend: { position: 'bottom', textStyle: { fontSize: 22 } },
      xAxis: { title: '세그먼트', textStyle: { fontSize: 23 } }, yAxis: { title: '비중', min: 0, max: .6, numberFormatCode: '0%', textStyle: { fontSize: 23 } },
      dataLabels: { showValue: true, position: 'outEnd', numberFormatCode: '0.0%', textStyle: { fontSize: 21 } } });
    table(slide, ['그룹', '고객', 'R중앙', 'F중앙'], names.map(n => [n, data.profile[n].Customers, data.profile[n].Recency_median, data.profile[n].Frequency_median]), 985, 260, 545, 420, [175, 120, 125, 125], 24);
    text(slide, '고객 합계 1,000명\n금액 합계 202.212746', 985, 730, 545, 80, 28, C.blue, true);
  } else if (spec.kind === 'impute') {
    table(slide, ['그룹', '관측 입력', '대치 결과', '이유'], [['A', '10', '10', '관측 유지'], ['A', '30', '30', '관측 유지'], ['A', 'NaN', '20', '(10+30)/2'], ['없음', '50', '50', '관측 유지'], ['없음', 'NaN', '30', '(10+30+50)/3']], 70, 235, 875, 490, [180, 200, 200, 295], 27);
    text(slide, '그룹 평균 20\n대치 전 전체 평균 30\n기존 관측값 50 보존', 1010, 240, 520, 180, 33, C.blue, true);
    text(slide, '실제 누락 이미지9개를 대치\n미표본4,496개는 결측 유지\n\n대치 후 분산 축소 위험\n0.010424 → 0.010130\n상관은 관측 상품만 사용', 1010, 465, 520, 310, 28);
  } else if (spec.kind === 'rfm') {
    table(slide, ['고객', '1월1일', '1월2일', '1월3일·기준일'], [['A', '10 + 20', '구매 없음', '30'], ['B', '구매 없음', '5', '구매 없음']], 70, 230, 1460, 240, [200, 420, 420, 420], 29);
    table(slide, ['고객', 'R 일', 'F 구매일', 'M 원금액'], [['A', '0', '2', '60'], ['B', '1', '1', '5']], 70, 525, 840, 230, [200, 210, 220, 210], 29);
    text(slide, 'R = 기준일 − 최종 구매일\nF = 날짜 nunique\nM = 유효 금액 sum\n전체 M = 65', 990, 550, 540, 225, 31, C.blue, true);
  } else if (spec.kind === 'score') {
    table(slide, ['F 예시', '평균순위', 'p', '점수'], [['1', '1.5', '.250', '1'], ['1', '1.5', '.250', '1'], ['2', '3.0', '.625', '3'], ['4', '4.0', '.875', '4']], 70, 250, 645, 400, [155, 190, 155, 145], 27);
    text(slide, '동일값은 동일 점수\n입력 행 순서를 바꿔도 동일\nR은 내림차순 순위 사용', 70, 700, 645, 110, 27, C.blue, true);
    table(slide, ['우선순위', '조건'], [['VIP', 'R/F/M 점수≥3, F원값≥2'], ['Loyal', 'R/F 점수≥3, F원값≥2'], ['New', 'R점수≥3, F원값=1'], ['Churned', 'R점수≤2'], ['Potential', '나머지']], 770, 250, 760, 490, [210, 550], 26);
  } else if (spec.kind === 'memory') {
    const strides = [['이미지 간', '12,288 B'], ['행 간', '384 B'], ['픽셀 간', '12 B'], ['채널 간', '4 B']];
    flow(slide, strides.map(row => row.join('\n')), 245, 130);
    code(slide, 'shape = (5, 32, 32, 3)\ndtype = float32\nstrides = (12288, 384, 12, 4)\nnbytes = 5 * 32 * 32 * 3 * 4 = 61440\nc_contiguous = True', 70, 450, 860, 300, 27);
    text(slide, '같은 자료형·연속 버퍼\nPython 픽셀별 호출 비용 감소\nNumPy 내부 루프·CPU 커널 활용\n\nSIMD 선택은 CPU·빌드·연산에 의존\n속도 배수는 측정 없이 주장하지 않음', 1000, 455, 530, 330, 29);
  } else if (spec.kind === 'scale') {
    flow(slide, ['고유 상품 파일 I/O', '원본 디코딩', '32×32 float32 축소', '제한 배치 통계'], 235, 135);
    table(slide, ['메모리 예', '픽셀 버퍼', '주의'], [['1024×1024 RGB float64 1장', '24 MiB', '가상 배열 입력의 크기'], ['위 고해상도 배열32장', '768 MiB', '전체 stack은 부담이 큼'], ['현재 축소 배치32장 상한', '384 KiB', '디코딩·중간 배열은 추가'], ['현재 표본의 최대5장 배치', '60 KiB', 'shape·dtype·stride 실제 확인']], 70, 435, 1460, 345, [620, 300, 540], 25);
  } else if (spec.kind === 'campaign') {
    const vip = node(slide, 'VIP 대상 후보\n고객270명 / 금액52.3%', 70, 250, 360, 150);
    const random = node(slide, '무작위 배정\n실험 설계·미실행', 535, 250, 350, 150);
    const treatment = node(slide, '발송군\n재입고·신상품 알림', 1010, 220, 520, 135, C.teal);
    const control = node(slide, '대조군\n동일 기간 미발송', 1010, 420, 520, 135, C.muted);
    connect(slide, vip, random); connect(slide, random, treatment, true); connect(slide, random, control, true);
    text(slide, 'KPI  이후30일 구매율 차이 / 고객당 마진 차이', 70, 610, 1460, 55, 32, C.blue, true);
    text(slide, '필요  연락 동의·반응·혜택 비용·마진·후속 거래\n리스크  자연 재구매 할인·계절성·재고 제약·표본 선택', 70, 690, 1460, 105, 30);
  } else if (spec.kind === 'timeline') {
    const before = node(slide, 'T 이전 관찰 구간\nRFM·상품 선호·이미지/텍스트 집계', 70, 250, 690, 170);
    const after = node(slide, 'T 이후30일 타겟 구간\n구매 여부 또는 원금액 합계', 840, 250, 690, 170, C.orange);
    connect(slide, before, after);
    text(slide, '피처 설계', 70, 490, 690, 48, 33, C.blue, true);
    text(slide, 'T까지만 계산한 R·F·M\n선호 상품군·이미지/텍스트 피처 평균\n이미지 관측률·결측 표시도 유지', 70, 560, 690, 225, 29);
    text(slide, '시간 누수·관측 중단', 840, 490, 690, 48, 33, C.orange, true);
    text(slide, '시간순 학습·검증, 대치 기준도 학습 구간\n미래30일 미관측 고객을0으로 라벨링하지 않음\n예측 모델 학습은 향후 확장안', 840, 560, 690, 225, 29);
  } else if (spec.kind === 'bonus_image') {
    chart(slide, 'bar', { position: { left: 70, top: 245, width: 900, height: 540 }, title: '관측200상품의 평균 정규화 히스토그램',
      categories: Array.from({ length: 8 }, (_, i) => `${(i / 8).toFixed(3)}~${((i + 1) / 8).toFixed(3)}`),
      series: [{ name: '픽셀 비중', values: data.bonus.image_features.histogram_mean, fill: C.blue }], hasLegend: false,
      xAxis: { title: '밝기 근사 8구간', textStyle: { fontSize: 19 } }, yAxis: { title: '평균 픽셀 비중', numberFormatCode: '0%', textStyle: { fontSize: 22 } },
      dataLabels: { showValue: true, position: 'outEnd', numberFormatCode: '0.0%', textStyle: { fontSize: 20 } } });
    text(slide, '각 이미지의 히스토그램 합 = 1\n마지막 구간은 밝기1 포함\n평균 엣지 = 0.045633', 1015, 245, 515, 150, 29, C.blue, true);
    for (const [col, values, label] of [[0, [0, 0, 1, 1], '줄무늬 edge=0.5'], [1, [0, 1, 1, 0], '체커보드 edge=1']]) {
      values.forEach((value, i) => {
        const shape = node(slide, String(value), 1040 + col * 245 + (i % 2) * 75, 455 + Math.floor(i / 2) * 75, 75, 75);
        shape.fill = value ? '#FFFFFF' : '#132F4A'; shape.text.color = value ? C.ink : C.white;
      });
      text(slide, label, 1010 + col * 245, 635, 245, 60, 24, C.ink, true, 'center');
    }
    text(slide, '두 예시는 mean/std·히스토그램이 같아도\n공간 배치에 따른 엣지 값이 다르다.', 1015, 720, 515, 85, 25);
  } else if (spec.kind === 'cohort') {
    const c = data.bonus.cohort, names = Object.keys(c.sizes);
    const rows = names.map(name => [`${name}\nN=${c.sizes[name]}`, ...[0, 1, 2].map(age => c.retention[name][age] == null ? '미관측' : `${percent(c.retention[name][age])}\n${c.active_customers[name][age]}명`)]);
    const matrix = table(slide, ['첫 관찰 구매월', 'M0', 'M1', 'M2'], rows, 70, 250, 1050, 400, [360, 230, 230, 230], 29);
    names.forEach((name, row) => [0, 1, 2].forEach(age => { const cell = matrix.getCell(row + 1, age + 1), value = c.retention[name][age]; cell.fill = value == null ? '#F1F3F5' : value > .8 ? C.blue : '#D8ECF6'; cell.text.color = value > .8 ? C.white : C.ink; }));
    text(slide, '비율 = 해당 월 활동 고객 / M0 고객\n동일 고객·동일 월은 한 번만 집계\n\n관측 무구매 = 0\n미래 미관측 = NaN\n\n가입일·생애 첫 구매는 알 수 없음', 1170, 245, 360, 480, 27);
    text(slide, '첫 구매월은 현재 관찰 기간 안의 기준이다. 연속 생존율과 구분하며 더 긴 이력이 필요하다.', 70, 730, 1460, 80, 29, C.blue, true);
  } else if (spec.kind === 'interactive') {
    await picture(slide, bonus('rfm_interactive_preview.png'), 70, 205, 1000, 625);
    text(slide, '드래그  3D 회전\n스크롤  확대\n범례  그룹 표시 선택\nhover  원본 고객ID·RFM\n\n인터넷 없이1000좌표 확인\nJS 내장 HTML을 브라우저로 열기', 1120, 285, 410, 465, 29);
  } else if (spec.kind === 'commands') {
    code(slide, './.venv/Scripts/python.exe -B -m utils.run_checks --with-sample\n./.venv/Scripts/python.exe -B -m utils.publish_report\n./.venv/Scripts/python.exe -B -m utils.repository_checks\nInvoke-Item docs/results/bonus/rfm_interactive.html', 70, 235, 1460, 260, 28);
    table(slide, ['시연', '직접 확인할 근거'], [['작은 입력', '대치20/30/50, IQR[-1,7], RFM A=0/2/60'], ['전체 결과', '12셀·20테스트, 고객/월/금액 합계, 원본 실행 표·이미지'], ['보너스', '이미지 합1·엣지, 코호트 분모·미관측, Plotly 조작']], 70, 555, 1460, 245, [300, 1160], 26);
  } else if (spec.kind === 'sources') {
    table(slide, ['자료', '확인할 내용'], [['docs/a1_1_eval.md / .pdf', '평가 원문19문항과 보너스 기준'], ['README.md / docs/tech_study.md', '실제 결과·실행 화면·수식·용어·SRC'], ['docs/a1_1_evaluation_qa.md', '질문별 답변·시연·꼬리 질문'], ['src/pipeline.py / utils / tests', '계산 구현·상태 변화·손계산·경계 검증'], ['notebooks / docs/results', '원본 실행 출력·집계·차트·코호트·독립 HTML'], ['NumPy / Pandas 공식 문서', 'strides·SIMD·std의 ddof·average rank']], 70, 225, 1460, 535, [610, 850], 26);
  }
  text(slide, `SRC  ${spec.source}`, 70, 846, 1380, 44, 18, C.muted);
  text(slide, `${index + 1} / ${specifications.length}`, 1450, 846, 90, 32, 18, C.muted, false, 'right');
  slide.speakerNotes.text = [spec.id ? `질문 번호: ${spec.id}` : spec.title,
    questions[spec.id] ? `평가 원문: ${questions[spec.id]}` : '',
    `발표 설명\n${spec.talk}`, `코드·화면 시연\n${spec.demo}`, `예상 꼬리 질문\n${spec.followup}`,
    `SRC\n${spec.source}`, '저장소: https://github.com/ntt65/A1_1', ...(spec.links || [])].filter(Boolean).join('\n\n');
}

const map = Object.entries(questions).map(([id, question]) => ({ id, question,
  slides: specifications.flatMap((slide, i) => slide.id === id ? [i + 1] : []) }));
await fs.writeFile(path.join(BUILD, 'question-map.json'), JSON.stringify({ slideCount: specifications.length, questions: map }, null, 2));
for (const [index, slide] of presentation.slides.items.entries()) {
  const png = await presentation.export({ slide, format: 'png', scale: 1 });
  await fs.writeFile(path.join(BUILD, `slide-${String(index + 1).padStart(2, '0')}.png`), new Uint8Array(await png.arrayBuffer()));
  console.log(`Rendered slide ${index + 1}/${specifications.length}`);
}
await (await PresentationFile.exportPptx(presentation)).save(path.join(BUILD, 'candidate.pptx'));
const result = await finalizePresentation({ workspaceDir: ROOT, candidatePath: path.join(BUILD, 'candidate.pptx'), finalPath: FINAL,
  pythonExecutable: path.resolve(options.python),
  integrityValidatorPath: path.join(options['skill-dir'], 'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath: path.join(options['skill-dir'], 'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs: ['--expected-slide-size-emu', '15240000,8572500', '--validate-bullet-geometry', '--validate-heading-fit',
    ...[...new Set(tableOwners)].flatMap(number => ['--require-native-table-slide', String(number)])],
  requiredNativeTableOwnerSlides: [...new Set(tableOwners)], requiredNativeChartOwnerSlides: [...new Set(chartOwners)],
  materializeLiteralChartWorkbooks: true,
  fontPolicy: { basis: 'design', families: [FONT] }, verifyArtifactToolImport: true,
  receiptPath: path.join(BUILD, `${path.basename(FINAL)}.validation.json`) });
await fs.writeFile(path.join(BUILD, 'finalizer-result.json'), JSON.stringify(result, null, 2));
const delivered = await PresentationFile.importPptx(await FileBlob.load(FINAL));
if (delivered.slides.items.length !== specifications.length) throw Error('Final slide count changed');
for (const [index, slide] of delivered.slides.items.entries()) {
  const png = await delivered.export({ slide, format: 'png', scale: 1 });
  await fs.writeFile(path.join(BUILD, `final-slide-${String(index + 1).padStart(2, '0')}.png`), new Uint8Array(await png.arrayBuffer()));
}
console.log('Final PPTX:', FINAL);
