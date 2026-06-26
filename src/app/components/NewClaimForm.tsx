import { useState, useRef, useCallback } from 'react';
import {
  Upload,
  X,
  ChevronLeft,
  Car,
  FileText,
  Image,
  AlertCircle,
  CheckCircle,
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import type { ViewType, ClaimFormData } from '../types';

interface NewClaimFormProps {
  onNavigate: (view: ViewType, data?: ClaimFormData) => void;
}

export function NewClaimForm({ onNavigate }: NewClaimFormProps) {
  const [form, setForm] = useState({
    vehicleMake: '',
    vehicleModel: '',
    policyNumber: '',
    accidentDescription: '',
  });
  const [images, setImages] = useState<File[]>([]);
  const [imagePreviews, setImagePreviews] = useState<string[]>([]);
  const [dragOver, setDragOver] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleChange = (field: string, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) setErrors((prev) => ({ ...prev, [field]: '' }));
  };

  const addImages = useCallback(
    (files: FileList | File[]) => {
      const valid = Array.from(files).filter((f) => f.type.startsWith('image/'));
      const newImages = [...images, ...valid].slice(0, 8);
      setImages(newImages);
      valid.forEach((file) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          setImagePreviews((prev) => [...prev, e.target?.result as string].slice(0, 8));
        };
        reader.readAsDataURL(file);
      });
    },
    [images]
  );

  const removeImage = (index: number) => {
    setImages((prev) => prev.filter((_, i) => i !== index));
    setImagePreviews((prev) => prev.filter((_, i) => i !== index));
  };

  const validate = () => {
    const newErrors: Record<string, string> = {};
    if (!form.vehicleMake.trim()) newErrors.vehicleMake = 'Vehicle make is required';
    if (!form.vehicleModel.trim()) newErrors.vehicleModel = 'Vehicle model is required';
    if (!form.policyNumber.trim()) newErrors.policyNumber = 'Policy number is required';
    if (!form.accidentDescription.trim() || form.accidentDescription.trim().length < 20)
      newErrors.accidentDescription = 'Please provide at least 20 characters';
    if (images.length === 0) newErrors.images = 'At least one vehicle image is required';
    return newErrors;
  };

  const handleSubmit = () => {
    const newErrors = validate();
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }
    setSubmitting(true);
    setTimeout(() => {
      onNavigate('processing', {
        vehicleMake: form.vehicleMake,
        vehicleModel: form.vehicleModel,
        policyNumber: form.policyNumber,
        accidentDescription: form.accidentDescription,
        images,
      });
    }, 600);
  };

  const inputClass = (field: string) =>
    `w-full px-4 py-3 rounded-xl border text-sm transition-all outline-none ${
      errors[field]
        ? 'border-red-300 bg-red-50 focus:border-red-400 focus:ring-2 focus:ring-red-100'
        : 'border-gray-200 bg-white focus:border-blue-400 focus:ring-2 focus:ring-blue-100'
    }`;

  return (
    <div
      className="min-h-full p-6"
      style={{ background: '#F0F4FF', fontFamily: "'Roboto', sans-serif" }}
    >
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <button
          onClick={() => onNavigate('dashboard')}
          className="w-9 h-9 rounded-xl flex items-center justify-center transition-colors"
          style={{ background: '#fff', boxShadow: '0 1px 4px rgba(0,0,0,0.1)' }}
        >
          <ChevronLeft className="w-4 h-4 text-gray-600" />
        </button>
        <div>
          <h1 className="text-gray-900" style={{ fontSize: 24, fontWeight: 600 }}>
            Submit New Claim
          </h1>
          <p className="text-gray-500 text-sm mt-0.5">
            AI-powered analysis will process your claim automatically
          </p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6 max-w-5xl">
        {/* Main Form */}
        <div className="col-span-2 space-y-5">
          {/* Vehicle Information Card */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl p-6"
            style={{ boxShadow: '0 1px 3px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.04)' }}
          >
            <div className="flex items-center gap-3 mb-5">
              <div
                className="w-9 h-9 rounded-xl flex items-center justify-center"
                style={{ background: '#EFF6FF' }}
              >
                <Car style={{ width: 18, height: 18, color: '#1976D2' }} />
              </div>
              <div>
                <h3 className="text-gray-900 text-sm" style={{ fontWeight: 600 }}>
                  Vehicle Information
                </h3>
                <p className="text-xs text-gray-400">Enter the insured vehicle details</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Vehicle Make <span className="text-red-400">*</span>
                </label>
                <input
                  className={inputClass('vehicleMake')}
                  placeholder="e.g. Toyota"
                  value={form.vehicleMake}
                  onChange={(e) => handleChange('vehicleMake', e.target.value)}
                />
                {errors.vehicleMake && (
                  <p className="text-xs text-red-500 mt-1 flex items-center gap-1">
                    <AlertCircle style={{ width: 11, height: 11 }} />
                    {errors.vehicleMake}
                  </p>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Vehicle Model <span className="text-red-400">*</span>
                </label>
                <input
                  className={inputClass('vehicleModel')}
                  placeholder="e.g. Camry 2022"
                  value={form.vehicleModel}
                  onChange={(e) => handleChange('vehicleModel', e.target.value)}
                />
                {errors.vehicleModel && (
                  <p className="text-xs text-red-500 mt-1 flex items-center gap-1">
                    <AlertCircle style={{ width: 11, height: 11 }} />
                    {errors.vehicleModel}
                  </p>
                )}
              </div>
              <div className="col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Policy Number <span className="text-red-400">*</span>
                </label>
                <input
                  className={inputClass('policyNumber')}
                  placeholder="e.g. POL-TY-88231"
                  value={form.policyNumber}
                  onChange={(e) => handleChange('policyNumber', e.target.value.toUpperCase())}
                />
                {errors.policyNumber && (
                  <p className="text-xs text-red-500 mt-1 flex items-center gap-1">
                    <AlertCircle style={{ width: 11, height: 11 }} />
                    {errors.policyNumber}
                  </p>
                )}
              </div>
            </div>
          </motion.div>

          {/* Accident Description Card */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 }}
            className="bg-white rounded-2xl p-6"
            style={{ boxShadow: '0 1px 3px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.04)' }}
          >
            <div className="flex items-center gap-3 mb-5">
              <div
                className="w-9 h-9 rounded-xl flex items-center justify-center"
                style={{ background: '#EFF6FF' }}
              >
                <FileText style={{ width: 18, height: 18, color: '#1976D2' }} />
              </div>
              <div>
                <h3 className="text-gray-900 text-sm" style={{ fontWeight: 600 }}>
                  Accident Description
                </h3>
                <p className="text-xs text-gray-400">Describe the incident in detail</p>
              </div>
            </div>
            <textarea
              className={`${inputClass('accidentDescription')} resize-none`}
              rows={5}
              placeholder="Describe the accident in detail — date, time, location, how it occurred, other parties involved, police report number (if any), and any immediate observations about the damage..."
              value={form.accidentDescription}
              onChange={(e) => handleChange('accidentDescription', e.target.value)}
            />
            <div className="flex items-center justify-between mt-1.5">
              {errors.accidentDescription ? (
                <p className="text-xs text-red-500 flex items-center gap-1">
                  <AlertCircle style={{ width: 11, height: 11 }} />
                  {errors.accidentDescription}
                </p>
              ) : (
                <span />
              )}
              <span className="text-xs text-gray-400 ml-auto">
                {form.accidentDescription.length} / 1000
              </span>
            </div>
          </motion.div>

          {/* Image Upload Card */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-2xl p-6"
            style={{ boxShadow: '0 1px 3px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.04)' }}
          >
            <div className="flex items-center gap-3 mb-5">
              <div
                className="w-9 h-9 rounded-xl flex items-center justify-center"
                style={{ background: '#EFF6FF' }}
              >
                <Image style={{ width: 18, height: 18, color: '#1976D2' }} />
              </div>
              <div>
                <h3 className="text-gray-900 text-sm" style={{ fontWeight: 600 }}>
                  Damage Images
                </h3>
                <p className="text-xs text-gray-400">
                  Upload up to 8 photos · AI Vision Agent will analyze them
                </p>
              </div>
            </div>

            {/* Drop Zone */}
            <div
              onClick={() => fileInputRef.current?.click()}
              onDragOver={(e) => {
                e.preventDefault();
                setDragOver(true);
              }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragOver(false);
                addImages(e.dataTransfer.files);
              }}
              className="border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all"
              style={{
                borderColor: dragOver ? '#1976D2' : errors.images ? '#FCA5A5' : '#DBEAFE',
                background: dragOver ? '#EFF6FF' : errors.images ? '#FFF5F5' : '#F8FBFF',
              }}
            >
              <div
                className="w-12 h-12 rounded-2xl flex items-center justify-center mx-auto mb-3"
                style={{ background: '#DBEAFE' }}
              >
                <Upload style={{ width: 20, height: 20, color: '#1976D2' }} />
              </div>
              <p className="text-sm font-medium text-gray-700">
                {dragOver ? 'Drop images here' : 'Drag & drop images, or click to browse'}
              </p>
              <p className="text-xs text-gray-400 mt-1">PNG, JPG, WEBP up to 10MB each · Max 8 images</p>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept="image/*"
                className="hidden"
                onChange={(e) => e.target.files && addImages(e.target.files)}
              />
            </div>
            {errors.images && (
              <p className="text-xs text-red-500 mt-2 flex items-center gap-1">
                <AlertCircle style={{ width: 11, height: 11 }} />
                {errors.images}
              </p>
            )}

            {/* Image Previews */}
            {imagePreviews.length > 0 && (
              <div className="grid grid-cols-4 gap-3 mt-4">
                <AnimatePresence>
                  {imagePreviews.map((src, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                      className="relative group rounded-xl overflow-hidden aspect-square bg-gray-100"
                    >
                      <img src={src} alt="" className="w-full h-full object-cover" />
                      <div className="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-colors" />
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          removeImage(i);
                        }}
                        className="absolute top-1.5 right-1.5 w-6 h-6 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                        style={{ background: '#EF4444' }}
                      >
                        <X style={{ width: 12, height: 12, color: '#fff' }} />
                      </button>
                      <div
                        className="absolute bottom-1.5 left-1.5 text-xs px-1.5 py-0.5 rounded-md"
                        style={{ background: 'rgba(0,0,0,0.5)', color: '#fff' }}
                      >
                        {i + 1}
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            )}
          </motion.div>
        </div>

        {/* Sidebar Summary */}
        <div className="space-y-4">
          {/* Submission Summary */}
          <motion.div
            initial={{ opacity: 0, x: 16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.15 }}
            className="bg-white rounded-2xl p-5"
            style={{ boxShadow: '0 1px 3px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.04)' }}
          >
            <h3 className="text-gray-900 text-sm mb-4" style={{ fontWeight: 600 }}>
              Claim Summary
            </h3>
            <div className="space-y-3">
              {[
                { label: 'Vehicle Make', value: form.vehicleMake || '—' },
                { label: 'Vehicle Model', value: form.vehicleModel || '—' },
                { label: 'Policy Number', value: form.policyNumber || '—' },
                { label: 'Images Attached', value: `${images.length} / 8` },
              ].map((item) => (
                <div key={item.label} className="flex justify-between items-start">
                  <span className="text-xs text-gray-400">{item.label}</span>
                  <span
                    className="text-xs font-medium text-gray-700 max-w-[60%] text-right truncate"
                  >
                    {item.value}
                  </span>
                </div>
              ))}
              <div className="pt-2 border-t border-gray-100">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-gray-400">Description</span>
                  <span className="text-xs font-medium text-gray-700">
                    {form.accidentDescription.length > 0
                      ? `${form.accidentDescription.length} chars`
                      : '—'}
                  </span>
                </div>
              </div>
            </div>
          </motion.div>

          {/* AI Processing Info */}
          <motion.div
            initial={{ opacity: 0, x: 16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="rounded-2xl p-5"
            style={{
              background: 'linear-gradient(135deg, #0D1B3E, #1565C0)',
              boxShadow: '0 4px 20px rgba(13,27,62,0.2)',
            }}
          >
            <h3 className="text-white text-sm mb-3" style={{ fontWeight: 600 }}>
              AI Processing Pipeline
            </h3>
            <div className="space-y-2.5">
              {[
                'Vision Agent analyzes images',
                'Damage Assessment evaluates parts',
                'Policy Analysis checks coverage',
                'Repair Estimation calculates costs',
                'Fraud Detection screens anomalies',
                'Decision Engine renders verdict',
              ].map((step, i) => (
                <div key={i} className="flex items-start gap-2">
                  <div
                    className="w-4 h-4 rounded-full flex items-center justify-center shrink-0 mt-0.5"
                    style={{ background: 'rgba(255,255,255,0.15)' }}
                  >
                    <span style={{ fontSize: 9, color: '#fff', fontWeight: 700 }}>{i + 1}</span>
                  </div>
                  <span className="text-xs" style={{ color: 'rgba(255,255,255,0.75)' }}>
                    {step}
                  </span>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Submit Button */}
          <motion.button
            initial={{ opacity: 0, x: 16 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.25 }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleSubmit}
            disabled={submitting}
            className="w-full flex items-center justify-center gap-2 py-3.5 rounded-xl font-medium text-white text-sm disabled:opacity-70"
            style={{
              background: submitting
                ? '#9CA3AF'
                : 'linear-gradient(135deg, #1565C0, #1976D2)',
              boxShadow: submitting ? 'none' : '0 4px 14px rgba(25, 118, 210, 0.4)',
            }}
          >
            {submitting ? (
              <>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
                  className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full"
                />
                Submitting…
              </>
            ) : (
              <>
                <CheckCircle className="w-4 h-4" />
                Submit Claim for AI Analysis
              </>
            )}
          </motion.button>
        </div>
      </div>
    </div>
  );
}
