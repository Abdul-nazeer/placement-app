import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useQuery } from '@tanstack/react-query';

import { useAuth } from '../../contexts/AuthContext';
import { AuthService } from '../../services/auth';
import { profileUpdateSchema, ProfileUpdateFormData } from '../../lib/validations';

const ProfileForm: React.FC = () => {
  const { user, updateProfile } = useAuth();

  // Fetch user profile
  const {
    data: profile,
    isLoading: isProfileLoading,
    error: profileError,
  } = useQuery({
    queryKey: ['userProfile'],
    queryFn: AuthService.getUserProfile,
    enabled: !!user,
  });

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting, isDirty },
  } = useForm({
    resolver: zodResolver(profileUpdateSchema),
  });

  // Reset form when profile data is loaded
  useEffect(() => {
    if (profile) {
      reset({
        college: profile.college || '',
        graduation_year: profile.graduation_year || undefined,
        target_companies: profile.target_companies || [],
        preferred_roles: profile.preferred_roles || [],
        skill_levels: profile.skill_levels || {},
        bio: profile.bio || '',
        phone: profile.phone || '',
        linkedin_url: profile.linkedin_url || '',
        github_url: profile.github_url || '',
      });
    }
  }, [profile, reset]);

  const onSubmit = async (data: ProfileUpdateFormData) => {
    try {
      // Clean up empty strings and convert to appropriate types
      const cleanedData = Object.entries(data).reduce((acc, [key, value]) => {
        if (value === '') {
          acc[key] = null;
        } else if (key === 'graduation_year' && value) {
          acc[key] = Number(value);
        } else {
          acc[key] = value;
        }
        return acc;
      }, {} as any);

      await updateProfile(cleanedData);
    } catch (error) {
      // Error is handled by the auth context
    }
  };

  if (isProfileLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (profileError) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">
              Error loading profile
            </h3>
            <div className="mt-2 text-sm text-red-700">
              <p>Unable to load your profile information. Please try again.</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-6">
            Profile Information
          </h3>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <label htmlFor="college" className="block text-sm font-medium text-gray-700">
                  College/University
                </label>
                <input
                  {...register('college')}
                  type="text"
                  className={`mt-1 block w-full px-3 py-2 border ${
                    errors.college ? 'border-red-300' : 'border-gray-300'
                  } rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm`}
                  placeholder="Enter your college or university"
                />
                {errors.college && (
                  <p className="mt-1 text-sm text-red-600">{errors.college.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="graduation_year" className="block text-sm font-medium text-gray-700">
                  Graduation Year
                </label>
                <input
                  {...register('graduation_year', { valueAsNumber: true })}
                  type="number"
                  min="1950"
                  max="2030"
                  className={`mt-1 block w-full px-3 py-2 border ${
                    errors.graduation_year ? 'border-red-300' : 'border-gray-300'
                  } rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm`}
                  placeholder="2024"
                />
                {errors.graduation_year && (
                  <p className="mt-1 text-sm text-red-600">{errors.graduation_year.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="phone" className="block text-sm font-medium text-gray-700">
                  Phone Number
                </label>
                <input
                  {...register('phone')}
                  type="tel"
                  className={`mt-1 block w-full px-3 py-2 border ${
                    errors.phone ? 'border-red-300' : 'border-gray-300'
                  } rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm`}
                  placeholder="+1234567890"
                />
                {errors.phone && (
                  <p className="mt-1 text-sm text-red-600">{errors.phone.message}</p>
                )}
              </div>

              <div>
                <label htmlFor="linkedin_url" className="block text-sm font-medium text-gray-700">
                  LinkedIn Profile
                </label>
                <input
                  {...register('linkedin_url')}
                  type="url"
                  className={`mt-1 block w-full px-3 py-2 border ${
                    errors.linkedin_url ? 'border-red-300' : 'border-gray-300'
                  } rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm`}
                  placeholder="https://linkedin.com/in/yourprofile"
                />
                {errors.linkedin_url && (
                  <p className="mt-1 text-sm text-red-600">{errors.linkedin_url.message}</p>
                )}
              </div>

              <div className="sm:col-span-2">
                <label htmlFor="github_url" className="block text-sm font-medium text-gray-700">
                  GitHub Profile
                </label>
                <input
                  {...register('github_url')}
                  type="url"
                  className={`mt-1 block w-full px-3 py-2 border ${
                    errors.github_url ? 'border-red-300' : 'border-gray-300'
                  } rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm`}
                  placeholder="https://github.com/yourusername"
                />
                {errors.github_url && (
                  <p className="mt-1 text-sm text-red-600">{errors.github_url.message}</p>
                )}
              </div>
            </div>

            <div>
              <label htmlFor="bio" className="block text-sm font-medium text-gray-700">
                Bio
              </label>
              <textarea
                {...register('bio')}
                rows={4}
                className={`mt-1 block w-full px-3 py-2 border ${
                  errors.bio ? 'border-red-300' : 'border-gray-300'
                } rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm`}
                placeholder="Tell us about yourself..."
              />
              {errors.bio && (
                <p className="mt-1 text-sm text-red-600">{errors.bio.message}</p>
              )}
            </div>

            <div className="flex justify-end">
              <button
                type="submit"
                disabled={isSubmitting || !isDirty}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Saving...
                  </div>
                ) : (
                  'Save Changes'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ProfileForm;