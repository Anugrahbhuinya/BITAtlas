import { useState, useEffect } from "react";
import { 
  User, Mail, GraduationCap, Calendar, 
  Hash, BookOpen, UserCheck, Edit2, Camera, 
  ShieldAlert, CheckCircle2, Loader2, ArrowLeft 
} from "lucide-react";
import { Link } from "react-router-dom";
import studentService from "../services/studentService";
import { useAuth } from "../../auth/hooks/useAuth";
import type { StudentUser } from "../../auth/types";

export const ProfilePage = () => {
  const { refreshProfile } = useAuth();
  
  const [profile, setProfile] = useState<StudentUser | null>(null);
  const [loadingProfile, setLoadingProfile] = useState(true);
  
  // Edit Profile States
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState("");
  const [editEmail, setEditEmail] = useState("");
  const [editError, setEditError] = useState<string | null>(null);
  const [editSuccess, setEditSuccess] = useState<string | null>(null);
  const [isSavingProfile, setIsSavingProfile] = useState(false);

  // Avatar Upload States
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const fetchProfileData = async () => {
    try {
      setLoadingProfile(true);
      const data = await studentService.getProfile();
      setProfile(data);
      setEditName(data.name);
      setEditEmail(data.email);
    } catch (e) {
      console.error("Failed to fetch profile details", e);
    } finally {
      setLoadingProfile(false);
    }
  };

  useEffect(() => {
    fetchProfileData();
  }, []);

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setEditError(null);
    setEditSuccess(null);

    if (!editName.trim() || !editEmail.trim()) {
      setEditError("Name and Email are required fields.");
      return;
    }

    setIsSavingProfile(true);
    try {
      const updated = await studentService.updateProfile({
        name: editName.trim(),
        email: editEmail.trim(),
      });
      setProfile(updated);
      await refreshProfile(); // Sync details to AuthContext/Sidebar
      setEditSuccess("Profile updated successfully!");
      setTimeout(() => {
        setIsEditing(false);
        setEditSuccess(null);
      }, 1500);
    } catch (err: any) {
      console.error("Edit profile failed:", err);
      const msg = err.response?.data?.detail || "Failed to update profile. Please verify your inputs.";
      setEditError(msg);
    } finally {
      setIsSavingProfile(false);
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadError(null);
    setUploadSuccess(null);

    // Validate size (5MB limit)
    if (file.size > 5 * 1024 * 1024) {
      setUploadError("File size exceeds 5MB limit.");
      return;
    }

    // Validate extension
    const ext = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();
    if (![".png", ".jpg", ".jpeg"].includes(ext)) {
      setUploadError("Only PNG, JPG, and JPEG images are allowed.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setIsUploading(true);
    try {
      const response = await studentService.uploadProfilePicture(formData);
      if (profile) {
        setProfile({
          ...profile,
          profile_picture: response.profile_picture,
        });
      }
      await refreshProfile(); // Sync details to AuthContext/Sidebar
      setUploadSuccess("Avatar updated successfully!");
      setTimeout(() => setUploadSuccess(null), 3000);
    } catch (err: any) {
      console.error("Avatar upload failed:", err);
      const msg = err.response?.data?.detail || "Failed to upload avatar.";
      setUploadError(msg);
    } finally {
      setIsUploading(false);
    }
  };

  if (loadingProfile) {
    return (
      <div className="h-[calc(100vh-4rem)] w-full flex flex-col items-center justify-center bg-background text-primary min-h-[500px]">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
        <p className="mt-4 text-xs font-bold uppercase tracking-wider text-on-surface-variant">Loading profile...</p>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="p-8 text-center text-on-surface bg-background min-h-[500px]">
        <p className="text-red-400 text-sm font-semibold">Failed to load student profile details.</p>
        <Link to="/" className="text-primary hover:underline mt-4 inline-block text-xs font-bold uppercase tracking-wider">Return to Dashboard</Link>
      </div>
    );
  }

  return (
    <div className="max-w-[1000px] mx-auto px-6 py-8 space-y-8 text-on-surface font-sans select-text">
      
      {/* Header Area */}
      <header className="border-b border-outline-variant/30 pb-6">
        <h1 className="text-xl font-extrabold text-primary flex items-center gap-2">
          <User className="w-5 h-5 text-primary shrink-0" />
          <span>Student Profile</span>
        </h1>
        <p className="text-on-surface-variant mt-1.5 text-xs md:text-sm">
          Manage your personal records, avatar, and security settings.
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Profile picture card */}
        <div className="md:col-span-1 matte-card rounded-2xl p-6 flex flex-col items-center justify-center min-h-[280px]">
          <div className="relative group mb-6 select-none">
            <div className="w-28 h-28 rounded-full overflow-hidden border border-outline-variant bg-surface-container flex items-center justify-center text-on-surface-variant">
              {profile.profile_picture ? (
                <img 
                  src={`http://localhost:8000${profile.profile_picture}`} 
                  alt={profile.name} 
                  className="w-full h-full object-cover"
                />
              ) : (
                <User className="w-12 h-12" />
              )}
            </div>

            {/* Upload trigger overlay */}
            <label className="absolute inset-0 bg-background/80 rounded-full flex flex-col items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer text-[10px] font-bold uppercase tracking-wider text-primary">
              <Camera className="w-4 h-4 mb-1 text-primary" />
              <span>Change Photo</span>
              <input 
                type="file" 
                accept="image/png, image/jpeg, image/jpg" 
                onChange={handleFileChange} 
                disabled={isUploading}
                className="hidden" 
              />
            </label>

            {isUploading && (
              <div className="absolute inset-0 bg-background/75 rounded-full flex items-center justify-center">
                <Loader2 className="w-6 h-6 animate-spin text-primary" />
              </div>
            )}
          </div>

          <h3 className="text-sm font-bold text-center text-primary leading-tight">{profile.name}</h3>
          <p className="text-[10px] text-on-surface-variant font-mono-code mt-1">{profile.roll_number}</p>

          <div className="w-full mt-4 space-y-2 select-none">
            {uploadError && (
              <p className="text-[10px] text-red-400 bg-red-500/10 border border-red-500/20 p-2 rounded-xl flex items-center gap-1.5 justify-center font-semibold">
                <ShieldAlert size={12} />
                <span>{uploadError}</span>
              </p>
            )}
            {uploadSuccess && (
              <p className="text-[10px] text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 p-2 rounded-xl flex items-center gap-1.5 justify-center font-semibold">
                <CheckCircle2 size={12} />
                <span>{uploadSuccess}</span>
              </p>
            )}
          </div>
        </div>

        {/* Details Cards */}
        <div className="md:col-span-2 space-y-6">
          
          {/* Personal info form */}
          <div className="matte-card rounded-2xl p-6 relative">
            <div className="flex items-center justify-between mb-6 pb-3 border-b border-outline-variant/30 select-none">
              <h2 className="text-xs font-bold uppercase tracking-wider text-primary">Personal Information</h2>
              {!isEditing && (
                <button
                  onClick={() => setIsEditing(true)}
                  className="flex items-center gap-1 px-3 py-1.5 bg-surface-container border border-outline-variant hover:border-primary text-primary text-[10px] font-bold uppercase tracking-wider rounded-lg transition-colors cursor-pointer"
                >
                  <Edit2 size={10} />
                  <span>Edit Profile</span>
                </button>
              )}
            </div>

            {isEditing ? (
              <form onSubmit={handleEditSubmit} className="space-y-4">
                <div className="space-y-2">
                  <label className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider block">Full Name</label>
                  <input
                    type="text"
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    required
                    className="w-full px-4 py-3 bg-surface-container border border-outline-variant focus:border-primary rounded-xl focus:outline-none transition-all text-on-surface text-xs font-semibold"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider block">Email Address</label>
                  <input
                    type="email"
                    value={editEmail}
                    onChange={(e) => setEditEmail(e.target.value)}
                    required
                    className="w-full px-4 py-3 bg-surface-container border border-outline-variant focus:border-primary rounded-xl focus:outline-none transition-all text-on-surface text-xs font-semibold"
                  />
                </div>

                {editError && (
                  <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl flex items-start gap-2 text-red-400 text-xs">
                    <ShieldAlert size={14} className="shrink-0 mt-0.5" />
                    <span>{editError}</span>
                  </div>
                )}

                {editSuccess && (
                  <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-start gap-2 text-emerald-400 text-xs">
                    <CheckCircle2 size={14} className="shrink-0 mt-0.5" />
                    <span>{editSuccess}</span>
                  </div>
                )}

                <div className="flex items-center gap-3 justify-end pt-2 select-none">
                  <button
                    type="button"
                    onClick={() => {
                      setIsEditing(false);
                      setEditName(profile.name);
                      setEditEmail(profile.email);
                      setEditError(null);
                    }}
                    className="px-4 py-2 border border-outline-variant hover:border-primary rounded-xl transition-colors text-[10px] font-bold uppercase tracking-wider cursor-pointer"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isSavingProfile}
                    className="px-4 py-2 bg-primary text-background rounded-xl hover:bg-primary/90 transition-colors text-[10px] font-bold uppercase tracking-wider flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                  >
                    {isSavingProfile && <Loader2 size={10} className="animate-spin" />}
                    <span>Save Changes</span>
                  </button>
                </div>
              </form>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
                <div className="flex items-center gap-3">
                  <User className="w-4 h-4 text-on-surface-variant/70 shrink-0" />
                  <div>
                    <span className="text-[10px] text-on-surface-variant block font-bold uppercase tracking-wider">Full Name</span>
                    <span className="text-on-surface font-semibold">{profile.name}</span>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <Mail className="w-4 h-4 text-on-surface-variant/70 shrink-0" />
                  <div>
                    <span className="text-[10px] text-on-surface-variant block font-bold uppercase tracking-wider">Email Address</span>
                    <span className="text-on-surface font-semibold">{profile.email}</span>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <Hash className="w-4 h-4 text-on-surface-variant/70 shrink-0" />
                  <div>
                    <span className="text-[10px] text-on-surface-variant block font-bold uppercase tracking-wider">Roll Number</span>
                    <span className="text-on-surface font-mono-code font-semibold">{profile.roll_number}</span>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <UserCheck className="w-4 h-4 text-on-surface-variant/70 shrink-0" />
                  <div>
                    <span className="text-[10px] text-on-surface-variant block font-bold uppercase tracking-wider">Account Status</span>
                    <span className="inline-flex px-2 py-0.5 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[9px] font-bold rounded-md uppercase tracking-wider mt-0.5">
                      {profile.status}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Academic details */}
          <div className="matte-card rounded-2xl p-6">
            <h2 className="text-xs font-bold uppercase tracking-wider text-primary mb-6 pb-3 border-b border-outline-variant/30 select-none">Academic Status</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
              <div className="flex items-center gap-3">
                <GraduationCap className="w-4 h-4 text-on-surface-variant/70 shrink-0" />
                <div>
                  <span className="text-[10px] text-on-surface-variant block font-bold uppercase tracking-wider">Department</span>
                  <span className="text-on-surface font-semibold">{profile.department}</span>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <BookOpen className="w-4 h-4 text-on-surface-variant/70 shrink-0" />
                <div>
                  <span className="text-[10px] text-on-surface-variant block font-bold uppercase tracking-wider">Program</span>
                  <span className="text-on-surface font-semibold">{profile.program}</span>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <Calendar className="w-4 h-4 text-on-surface-variant/70 shrink-0" />
                <div>
                  <span className="text-[10px] text-on-surface-variant block font-bold uppercase tracking-wider">Year & Semester</span>
                  <span className="text-on-surface font-semibold">
                    Year {profile.year} — Semester {profile.semester}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <Hash className="w-4 h-4 text-on-surface-variant/70 shrink-0" />
                <div>
                  <span className="text-[10px] text-on-surface-variant block font-bold uppercase tracking-wider">Section</span>
                  <span className="text-on-surface font-mono-code font-semibold">Section {profile.section}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Key Change Password Button */}
          <div className="flex justify-end select-none">
            <Link 
              to="/profile/change-password"
              className="px-4 py-2 bg-surface-container border border-outline-variant hover:border-primary text-primary text-[10px] font-bold uppercase tracking-wider rounded-xl transition-colors cursor-pointer"
            >
              Change Account Password
            </Link>
          </div>

        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
