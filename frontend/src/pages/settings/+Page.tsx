import { useAuthContext } from '../../components/useAuthContext'
import { useState, useEffect } from 'react'
import { type MoodleSettings, type SchoolDistrict, ropeApi } from '../../utils/ropeApi'
import styled from 'styled-components'

const Container = styled.div`
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
`

const Title = styled.h2`
  color: #333;
  text-align: center;
  margin-bottom: 20px;
`

const SettingsContainer = styled.div`
  width: 100%;
  margin-bottom: 30px;
`

const Label = styled.label`
  display: flex;
  align-items: center;
  margin: 10px;
  width: 100%;
`

const Input = styled.input`
  margin-left: 10px;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  flex-grow: 1;
`

const Button = styled.button`
padding: 8px 16px;
`

const DistrictList = styled.ul`
  padding: 0;
  width: 100%;
`

const DistrictListItem = styled.li`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 10px 0;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
`

const StatusButtonGroup = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
`

const Message = styled.p`
  color: grey;
`

function Page(): JSX.Element {
  const authContext = useAuthContext()

  const [settings, setSettings] = useState<MoodleSettings[]>([
    { name: 'academic_year', value: '' },
    { name: 'academic_year_short', value: '' },
    { name: 'course_category', value: '' },
    { name: 'base_course_id', value: '' }
  ])
  const [districts, setDistricts] = useState<SchoolDistrict[]>([])
  const [newDistrictName, setNewDistrictName] = useState<string>('')
  const [settingsMessage, setSettingsMessage] = useState<string | null>(null)
  const [districtMessage, setDistrictMessage] = useState<string | null>(null)

  const fetchSettings = async (): Promise<void> => {
    try {
      const moodleSettings = await ropeApi.getMoodleSettings()
      const updatedSettings = settings.map(setting => {
        const foundSetting = moodleSettings.find(s => s.name === setting.name)
        return (foundSetting != null) ? { ...setting, value: foundSetting.value, id: foundSetting.id } : setting
      })
      setSettings(updatedSettings)
    } catch (error) {
      console.error('Error fetching districts', error)
    }
  }
  const fetchDistricts = async (): Promise<void> => {
    try {
      const districtsFromApi = await ropeApi.getDistricts()
      setDistricts(districtsFromApi)
    } catch (error) {
      console.error('Error fetching districts:', error)
    }
  }
  useEffect(() => {
    if (authContext.isAdmin) {
      void fetchSettings()
      void fetchDistricts()
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authContext.isAdmin])

  const handleInputChange = (index: number, value: string): void => {
    const updatedSettings = settings.map((setting, i) =>
      i === index ? { ...setting, value } : setting
    )
    setSettings(updatedSettings)
  }

  const saveSettings = async (): Promise<void> => {
    try {
      await Promise.all(settings.map(async setting => {
        if (setting.id !== undefined) {
          return await ropeApi.updateMoodleSettings(setting.id, { ...setting, value: setting.value })
        } else {
          const newSetting = await ropeApi.createMoodleSetting({ name: setting.name, value: setting.value })
          setting.id = newSetting.id
        }
      }))
      setSettingsMessage('Settings saved successfully')
    } catch (error) {
      console.error(error)
      setSettingsMessage('Failed to save settings')
    }
  }
  const handleAddDistrict = async (): Promise<void> => {
    if (newDistrictName.trim() === '') {
      setDistrictMessage('District name cannot be empty')
      return
    }
    try {
      const newDistrict: SchoolDistrict = await ropeApi.createDistrict({
        name: newDistrictName,
        active: true
      })
      setDistricts([...districts, newDistrict])
      setNewDistrictName('')
      setDistrictMessage('District added successfully')
    } catch (error) {
      console.error('Error adding district:', error)
      setDistrictMessage('Error adding district')
    }
  }

  const handleToggleActive = async (id: number, active: boolean, name: string): Promise<void> => {
    try {
      await ropeApi.updateDistrict(
        {
          id,
          active,
          name
        })
      setDistricts(districts.map(district => district.id === id ? { ...district, active } : district))
      setDistrictMessage(`District "${name}" updated successfully`)
    } catch (error) {
      console.error('Error updating district:', error)
      setDistrictMessage(`Error updating district "${name}"`)
    }
  }

  return (
    <Container>
    {authContext.isAdmin
      ? <>

      <Title>Moodle Settings</Title>
      <SettingsContainer>
        {settings.map((setting, index) => (
          <Label key={setting.name}>
            {setting.name.replace(/_/g, ' ')}:
            <Input
              type="text"
              placeholder={setting.name}
              value={setting.value}
              onChange={(e) => { handleInputChange(index, e.target.value) }}
            />
          </Label>
        ))}
      </SettingsContainer>
      <Button onClick={() => { void saveSettings() }}>Save Settings</Button>
      {(settingsMessage != null) && <Message>{settingsMessage}</Message>}

      <Title>District List</Title>
      <DistrictList>
        {districts.map(district => (
          <DistrictListItem key={district.id}>
            {district.name}
            <StatusButtonGroup>
              <span>Active: {district.active ? 'Yes' : 'No'}</span>
              <Button onClick={() => {
                if (district.id !== undefined) {
                  void handleToggleActive(district.id, !district.active, district.name)
                }
              }}>
                Toggle Active
              </Button>
            </StatusButtonGroup>
          </DistrictListItem>
        ))}
      </DistrictList>
      <Input
        type="text"
        value={newDistrictName}
        onChange={(e) => { setNewDistrictName(e.target.value) }}
        placeholder="Enter district name"
      />
      <Button onClick={() => { void handleAddDistrict() }}>Add District</Button>
      {(districtMessage != null) && <Message>{districtMessage}</Message>}
      </>

      : <p>This page is admin only</p>}
    </Container>
  )
}

export { Page }
