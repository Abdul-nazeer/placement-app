import { z } from 'zod';

// Password validation schema
const passwordSchema = z
  .string()
  .min(8, 'Password must be at least 8 characters long')
  .max(128, 'Password must be less than 128 characters long')
  .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
  .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
  .regex(/\d/, 'Password must contain at least one digit')
  .regex(/[!@#$%^&*(),.?":{}|<>]/, 'Password must contain at least one special character')
  .refine(
    (password: string) => {
      const commonPatterns = [
        /123456/,
        /password/i,
        /qwerty/i,
        /abc123/i,
        /admin/i,
        /letmein/i,
      ];
      return !commonPatterns.some((pattern) => pattern.test(password));
    },
    'Password contains common patterns and is not secure'
  );

// Login form validation
export const loginSchema = z.object({
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Please enter a valid email address'),
  password: z
    .string()
    .min(1, 'Password is required'),
});

// Registration form validation
export const registerSchema = z.object({
  name: z
    .string()
    .min(2, 'Name must be at least 2 characters long')
    .max(255, 'Name must be less than 255 characters long')
    .regex(/^[a-zA-Z\s]+$/, 'Name can only contain letters and spaces'),
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Please enter a valid email address'),
  password: passwordSchema,
  confirmPassword: z.string().min(1, 'Please confirm your password'),
  role: z.enum(['student', 'trainer', 'admin']).default('student'),
}).refine(
  (data: any) => data.password === data.confirmPassword,
  {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  }
);

// Password change validation
export const passwordChangeSchema = z.object({
  current_password: z.string().min(1, 'Current password is required'),
  new_password: passwordSchema,
  confirm_new_password: z.string().min(1, 'Please confirm your new password'),
}).refine(
  (data: any) => data.new_password === data.confirm_new_password,
  {
    message: 'New passwords do not match',
    path: ['confirm_new_password'],
  }
);

// Profile update validation
export const profileUpdateSchema = z.object({
  college: z
    .string()
    .max(255, 'College name must be less than 255 characters')
    .optional()
    .or(z.literal('')),
  graduation_year: z
    .number()
    .int()
    .min(1950, 'Graduation year must be after 1950')
    .max(2030, 'Graduation year must be before 2030')
    .optional()
    .nullable(),
  target_companies: z
    .array(z.string())
    .optional(),
  preferred_roles: z
    .array(z.string())
    .optional(),
  skill_levels: z
    .record(z.string(), z.number().int().min(1).max(10))
    .optional(),
  bio: z
    .string()
    .max(1000, 'Bio must be less than 1000 characters')
    .optional()
    .or(z.literal('')),
  phone: z
    .string()
    .max(20, 'Phone number must be less than 20 characters')
    .regex(/^[\+]?[1-9][\d]{0,15}$/, 'Please enter a valid phone number')
    .optional()
    .or(z.literal('')),
  linkedin_url: z
    .string()
    .url('Please enter a valid LinkedIn URL')
    .max(500, 'LinkedIn URL must be less than 500 characters')
    .optional()
    .or(z.literal('')),
  github_url: z
    .string()
    .url('Please enter a valid GitHub URL')
    .max(500, 'GitHub URL must be less than 500 characters')
    .optional()
    .or(z.literal('')),
});

// Type exports
export type LoginFormData = z.infer<typeof loginSchema>;
export type RegisterFormData = z.infer<typeof registerSchema>;
export type PasswordChangeFormData = z.infer<typeof passwordChangeSchema>;
export type ProfileUpdateFormData = z.infer<typeof profileUpdateSchema>;