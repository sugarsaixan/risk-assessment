/**
 * TypeScript type definitions for API contracts.
 * Based on specs/001-risk-assessment-survey/contracts/
 */

// ============================================================================
// Enums
// ============================================================================

export type ScoringMethod = "SUM";

export type RespondentKind = "ORG" | "PERSON";

export type OptionType = "YES" | "NO";

export type AssessmentStatus = "PENDING" | "COMPLETED" | "EXPIRED";

export type RiskRating = "LOW" | "MEDIUM" | "HIGH";

// ============================================================================
// Common Types
// ============================================================================

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface ErrorResponse {
  detail: string;
  code?: string;
}

// ============================================================================
// Questionnaire Types
// ============================================================================

export interface QuestionnaireType {
  id: string;
  name: string;
  scoring_method: ScoringMethod;
  threshold_high: number;
  threshold_medium: number;
  weight: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// Question Groups (Бүлэг)
// ============================================================================

export interface QuestionGroup {
  id: string;
  type_id: string;
  name: string;
  display_order: number;
  weight: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// Questions
// ============================================================================

export interface QuestionOption {
  id: string;
  question_id: string;
  option_type: OptionType;
  score: number;
  require_comment: boolean;
  require_image: boolean;
  comment_min_len: number;
  max_images: number;
  image_max_mb: number;
}

export interface Question {
  id: string;
  group_id: string;
  text: string;
  display_order: number;
  weight: number;
  is_critical: boolean;
  is_active: boolean;
  created_at?: string;
  options?: QuestionOption[];
}

// ============================================================================
// Respondents
// ============================================================================

export interface Respondent {
  id: string;
  kind: RespondentKind;
  name: string;
  registration_no?: string;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// Submission Contact (Хариулагч)
// ============================================================================

export interface SubmissionContactInput {
  last_name: string;
  first_name: string;
  email: string;
  phone: string;
  position: string;
}

export interface SubmissionContact extends SubmissionContactInput {
  id: string;
  assessment_id: string;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// Assessments
// ============================================================================

export interface Assessment {
  id: string;
  respondent_id: string;
  selected_type_ids: string[];
  expires_at: string;
  status: AssessmentStatus;
  completed_at?: string;
  created_at: string;
}

export interface AssessmentCreated {
  id: string;
  url: string;
  expires_at: string;
}

// ============================================================================
// Public Assessment Form (Snapshot) - Hierarchical Structure
// ============================================================================

export interface SnapshotOption {
  score: number;
  require_comment: boolean;
  require_image: boolean;
  comment_min_len: number;
  max_images: number;
  image_max_mb: number;
}

export interface SnapshotQuestion {
  id: string;
  text: string;
  display_order: number;
  weight: number;
  is_critical: boolean;
  options: {
    YES: SnapshotOption;
    NO: SnapshotOption;
  };
}

export interface SnapshotGroup {
  id: string;
  name: string;
  display_order: number;
  weight: number;
  questions: SnapshotQuestion[];
}

export interface SnapshotType {
  id: string;
  name: string;
  threshold_high: number;
  threshold_medium: number;
  weight: number;
  groups: SnapshotGroup[];
}

export interface AssessmentForm {
  id: string;
  respondent_name: string;
  expires_at: string;
  types: SnapshotType[];
}

// ============================================================================
// Submission
// ============================================================================

export interface AnswerInput {
  question_id: string;
  selected_option: OptionType;
  comment?: string;
  attachment_ids?: string[];
}

export interface SubmitRequest {
  contact: SubmissionContactInput;
  answers: AnswerInput[];
}

// ============================================================================
// Results - Hierarchical Structure
// ============================================================================

export interface GroupResult {
  group_id: string;
  group_name: string;
  raw_score: number;
  max_score: number;
  percentage: number;
  risk_rating: RiskRating;
}

export interface TypeResult {
  type_id: string;
  type_name: string;
  raw_score: number;
  max_score: number;
  percentage: number;
  risk_rating: RiskRating;
  groups: GroupResult[];
}

export interface OverallResult {
  raw_score: number;
  max_score: number;
  percentage: number;
  risk_rating: RiskRating;
}

export interface SubmitResponse {
  assessment_id: string;
  type_results: TypeResult[];
  overall_result: OverallResult;
}

// ============================================================================
// Attachments
// ============================================================================

export interface AttachmentUpload {
  id: string;
  original_name: string;
  size_bytes: number;
  mime_type: string;
}
