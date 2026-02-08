/**
 * Mongolian Cyrillic string constants for the assessment UI.
 */

export const MN = {
  // Common
  loading: "Уншиж байна...",
  error: "Алдаа гарлаа",
  submit: "Илгээх",
  cancel: "Цуцлах",

  // Assessment Form
  assessment: {
    title: "Эрсдэлийн үнэлгээ",
    questionCount: (current: number, total: number) => `${current} / ${total} асуулт`,
    requiredComment: "Тайлбар оруулах шаардлагатай",
    requiredImage: "Зураг оруулах шаардлагатай",
    minCommentLength: (min: number) => `Хамгийн багадаа ${min} тэмдэгт`,
    maxCommentLength: (max: number) => `Хамгийн ихдээ ${max} тэмдэгт`,
    characterCount: (current: number, max: number) => `${current} / ${max}`,
    submitAssessment: "Үнэлгээг илгээх",
    submitting: "Илгээж байна...",
  },

  // Answer Options
  options: {
    yes: "Тийм",
    no: "Үгүй",
  },

  // Image Upload
  upload: {
    dragDrop: "Зургаа энд чирж тавина уу",
    or: "эсвэл",
    browse: "Файл сонгох",
    uploading: "Байршуулж байна...",
    uploadComplete: "Байршуулалт дууссан",
    maxSize: (mb: number) => `Хамгийн их хэмжээ: ${mb}MB`,
    maxImages: (count: number) => `Хамгийн ихдээ ${count} зураг`,
    allowedTypes: "Зөвшөөрөгдсөн төрөл: JPEG, PNG, GIF, WebP",
    remove: "Устгах",
    invalidType: "Зөвшөөрөгдөөгүй файлын төрөл",
    fileTooLarge: "Файл хэт том байна",
  },

  // Results
  results: {
    title: "Үнэлгээний үр дүн",
    overall: "Нийт үр дүн",
    typeResults: "Төрөл тус бүрийн үр дүн",
    score: "Оноо",
    percentage: "Хувь",
    riskLevel: "Эрсдэлийн түвшин",
    lowRisk: "Бага эрсдэл",
    mediumRisk: "Дунд эрсдэл",
    highRisk: "Өндөр эрсдэл",
    completedAt: "Дуусгасан огноо",
  },

  // Answers Section
  answers: {
    title: "Хариултууд",
    show: "Хариултуудыг харах",
    hide: "Хариултуудыг нуух",
    attachments: "Хавсралт",
    yes: "Тийм",
    no: "Үгүй",
  },

  // Risk Ratings (Mongolian labels)
  riskRating: {
    LOW: "Бага",
    MEDIUM: "Дунд",
    HIGH: "Өндөр",
  },

  // Error Pages
  errors: {
    notFound: {
      title: "Олдсонгүй",
      message: "Үнэлгээ олдсонгүй.",
    },
    expired: {
      title: "Хугацаа дууссан",
      message: "Линкний хугацаа дууссан байна.",
    },
    alreadyCompleted: {
      title: "Ашиглагдсан",
      message: "Энэ линк аль хэдийн ашиглагдсан байна.",
    },
    generic: {
      title: "Алдаа",
      message: "Системийн алдаа гарлаа. Дахин оролдоно уу.",
    },
  },

  // Validation Errors
  validation: {
    required: "Энэ талбарыг бөглөх шаардлагатай",
    minLength: (min: number) => `Хамгийн багадаа ${min} тэмдэгт шаардлагатай`,
    maxLength: (max: number) => `${max} тэмдэгтээс хэтрэхгүй байх ёстой`,
    invalidFormat: "Буруу формат",
    answerRequired: "Бүх асуултад хариулна уу",
  },
} as const;
